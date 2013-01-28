#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file write for SES3D 4.0

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
EARTH_RADIUS = 6371 * 1000

from wfs_input_generator import rotations

import os


def write(config, events, stations, output_directory):
    """
    Writes input files for SES3D version 4.0.

    Can only simulate one event at a time. If more events are present, an error
    will be raised.
    """
    # Optional parameters.
    config.setdefault("snapshot_sampling", 10000)
    config.setdefault("output_displacement", False)
    config.setdefault("is_dissipative", False)
    config.setdefault("model_type", 1)
    config.setdefault("lagrange_polynomial_degree", 4)
    # Can be one of
    #    * "normal simulation"
    #    * "adjoint forward"
    #    * "adjoint reverse"
    config.setdefault("simulation_type", "normal simulation")
    # Set the sampling rate of the forward field for the adjoint simulation.
    config.setdefault("adj_forward_sampling_rate", 15)

    # Define the rotation axis. The rotation is the rotation of the mesh. The
    # data will be rotated in the inverse direction!
    config.mesh.setdefault("rotation_axis", [0, 0, 1])
    config.mesh.setdefault("rotation_angle", 0.0)

    rotation_angle = config.mesh.rotation_angle
    if rotation_angle:
        rotation_angle *= -1
    rotation_axis = config.mesh.rotation_axis

    # Parse the simulation type.
    sim_map = {
        "normal simulation": 0,
        "adjoint forward": 1,
        "adjoint reverse": 2}
    if config.simulation_type not in sim_map:
        msg = "simulation_type needs to be on of %s." % \
            ", ".join(sim_map.keys())
        raise ValueError(msg)
    simulation_type = sim_map[config.simulation_type]

    # Create subfolders.
    input_folder = os.path.join(output_directory, "INPUT")
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    # One exactly one event is acceptable.
    if len(events) != 1:
        msg = "Exactly one event is needed"
        raise ValueError(msg)
    event = events[0]

    # Rotate coordinates and moment tensor if requested.
    if rotation_angle:
        lat, lng = rotations.rotate_lat_lon(event["latitude"],
                event["longitude"], rotation_axis, rotation_angle)
        m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = rotations.rotate_moment_tensor(
            event["m_rr"], event["m_tt"], event["m_pp"], event["m_rt"],
            event["m_rp"], event["m_tp"], event["latitude"],
            event["longitude"], rotation_axis, rotation_angle)
    else:
        lat, lng = (event["latitude"], event["longitude"])
        m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = (event["m_rr"], event["m_tt"],
            event["m_pp"], event["m_rt"], event["m_rp"], event["m_tp"])

    event_template = (
    "SIMULATION PARAMETERS =================================================="
        "================================\n"
    "{nt:<56d}! nt, number of time steps\n"
    "{dt:<56.6f}! dt in sec, time increment\n"
    "SOURCE ================================================================="
        "================================\n"
    "{xxs:<56.6f}! xxs, theta-coord. center of source in degrees\n"
    "{yys:<56.6f}! yys, phi-coord. center of source in degrees\n"
    "{zzs:<56.6f}! zzs, source depth in (m)\n"
    "{srctype:<56d}! srctype, 1:f_x, 2:f_y, 3:f_z, 10:M_ij\n"
    "{m_tt:<56.6e}! M_theta_theta\n"
    "{m_pp:<56.6e}! M_phi_phi\n"
    "{m_rr:<56.6e}! M_r_r\n"
    "{m_tp:<56.6e}! M_theta_phi\n"
    "{m_tr:<56.6e}! M_theta_r\n"
    "{m_pr:<56.6e}! M_phi_r\n"
    "OUTPUT DIRECTORY ======================================================="
        "===============================\n"
    "{output_directory}\n"
    "OUTPUT FLAGS ==========================================================="
        "===============================\n"
    "{ssamp:<56d}! ssamp, snapshot sampling\n"
    "{output_displacement:<56d}! output_displacement, output displacement "
        "field (1=yes,0=no)")

    event_file = event_template.format(
        nt=config.time_config.time_steps,
        dt=config.time_config.time_delta,
        # Colatitude!
        xxs=90.0 - lat,
        yys=lng,
        zzs=event["depth_in_km"] * 1000.0,
        srctype=10,
        m_tt=m_tt,
        m_pp=m_pp,
        m_rr=m_rr,
        m_tp=m_tp,
        m_tr=m_rt,
        m_pr=m_rp,
        output_directory=config.output_directory,
        ssamp=int(config.snapshot_sampling),
        output_displacement=1 if config.output_displacement else 0)

    # Write the event file.
    with open(os.path.join(input_folder, "event_1"), "wt") as open_file:
        open_file.write(event_file)

    # Write the event_list file
    with open(os.path.join(input_folder, "event_list"), "wt") as open_file:
        open_file.write("{0:<56d}! n_events = number_of_events\n{0}".format(1))

    recfile_parts = [str(len(stations))]
    for station in stations:
        # Also rotate each station if desired.
        if rotation_angle:
            lat, lng = rotations.rotate_lat_lon(station["latitude"],
                station["longitude"], rotation_axis, rotation_angle)
        else:
            lat, lng = (station["latitude"], station["longitude"])

        depth = -1.0 * (station["elevation_in_m"] - \
            station["local_depth_in_m"])
        if depth < 0:
            depth = 0.0
        recfile_parts.append("{network:_<2s}.{station:_<5s}.___".format(
            network=station["id"].split(".")[0],
            station=station["id"].split(".")[1]))
        recfile_parts.append("{colatitude:.6f} {longitude:.6f} {depth:.1f}"\
            .format(colatitude=90.0 - lat, longitude=lng, depth=depth))

    # Write the receiver file.
    with open(os.path.join(input_folder, "recfile"), "wt") as open_file:
        open_file.write("\n".join(recfile_parts))

    # Write the currently hardcoded relaxation file.
    relax_file = (
        "RELAXATION TIMES [s] =====================\n"
        "1.7308\n"
        "14.3961\n"
        "22.9973\n"
        "WEIGHTS OF RELAXATION MECHANISMS =========\n"
        "2.5100\n"
        "2.4354\n"
        "0.0879")
    with open(os.path.join(input_folder, "relax"), "wt") as open_file:
        open_file.write(relax_file)

    setup_file_template = (
        "MODEL ==============================================================="
            "================================================================="
            "=====\n"
        "{theta_min:<56.6f}! theta_min (colatitude) in degrees\n"
        "{theta_max:<56.6f}! theta_max (colatitude) in degrees\n"
        "{phi_min:<56.6f}! phi_min (longitude) in degrees\n"
        "{phi_max:<56.6f}! phi_max (longitude) in degrees\n"
        "{z_min:<56.6f}! z_min (radius) in m\n"
        "{z_max:<56.6f}! z_max (radius) in m\n"
        "{is_diss:<56d}! is_diss\n"
        "{model_type:<56d}! model_type\n"
        "COMPUTATIONAL SETUP (PARALLELISATION) ==============================="
            "================================================================="
            "=====\n"
        "{nx_global:<56d}! nx_global, "
            "(nx_global+px = global # elements in theta direction)\n"
        "{ny_global:<56d}! ny_global, "
            "(ny_global+py = global # elements in phi direction)\n"
        "{nz_global:<56d}! nz_global, "
            "(nz_global+pz = global # of elements in r direction)\n"
        "{lpd:<56d}! lpd, LAGRANGE polynomial degree\n"
        "{px:<56d}! px, processors in theta direction\n"
        "{py:<56d}! py, processors in phi direction\n"
        "{pz:<56d}! pz, processors in r direction\n"
        "ADJOINT PARAMETERS =================================================="
            "================================================================="
            "=====\n"
        "{adjoint_flag:<56d}! adjoint_flag (0=normal simulation, "
            "1=adjoint forward, 2=adjoint reverse)\n"
        "{samp_ad:<56.2f}! samp_ad, sampling rate of forward field\n"
        "{wavefield_folder}")

    setup_file = setup_file_template.format(
        # Colatitude!
        theta_min=90.0 - config.mesh.min_latitude,
        theta_max=90.0 - config.mesh.max_latitude,
        phi_min=config.mesh.min_longitude,
        phi_max=config.mesh.max_longitude,
        ## Min/max radius and depth are inverse to each other.
        z_min=EARTH_RADIUS - (config.mesh.max_depth * 1000.0),
        z_max=EARTH_RADIUS - (config.mesh.min_depth * 1000.0),
        is_diss=1 if config.is_dissipative else 0,
        model_type=1,
        lpd=config.lagrange_polynomial_degree,
        # Computation setup.
        nx_global=config.nx_global,
        ny_global=config.ny_global,
        nz_global=config.nz_global,
        px=config.px,
        py=config.py,
        pz=config.pz,
        adjoint_flag=simulation_type,
        samp_ad=config.adj_forward_sampling_rate,
        wavefield_folder=config.forward_wavefield_output_folder)

    with open(os.path.join(input_folder, "setup"), "wt") as open_file:
        open_file.write(setup_file)

    return
