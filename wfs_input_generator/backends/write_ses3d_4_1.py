#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file writer for SES3D 4.1.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import numpy as np
import obspy
import os
from wfs_input_generator import rotations

EARTH_RADIUS = 6371 * 1000


# Define the required configuration items. The key is always the name of the
# configuration item and the value is a tuple. The first item in the tuple is
# the function or type that it will be converted to and the second is the
# documentation.
REQUIRED_CONFIGURATION = {
    "output_folder": (str, "The output directory"),
    "number_of_time_steps": (int, "The number of time steps"),
    "time_increment_in_s": (float, "The time increment in seconds"),
    "mesh_min_latitude": (float, "The minimum latitude of the mesh"),
    "mesh_max_latitude": (float, "The maximum latitude of the mesh"),
    "mesh_min_longitude": (float, "The minimum longitude of the mesh"),
    "mesh_max_longitude": (float, "The maximum longitude of the mesh"),
    "mesh_min_depth_in_km": (float, "The minimum depth of the mesh in km"),
    "mesh_max_depth_in_km": (float, "The maximum depth of the mesh in km"),
    "nx_global": (int, "Number of elements in theta directions. Please refer "
                  "to the SES3D manual for a more extensive description"),
    "ny_global": (int, "Number of elements in phi directions. Please refer "
                  "to the SES3D manual for a more extensive description"),
    "nz_global": (int, "Number of elements in r directions. Please refer "
                  "to the SES3D manual for a more extensive description"),
    "px": (int, "Number of processors in theta direction"),
    "py": (int, "Number of processors in phi direction"),
    "pz": (int, "Number of processors in r direction"),
    "source_time_function": (np.array, "The source time function.")
}

# The default configuration item. Contains everything that can sensibly be set
# to some default value. The syntax is very similar to the
# REQUIRED_CONFIGURATION except that the tuple now has three items, the first
# one being the actual default value.
DEFAULT_CONFIGURATION = {
    "event_tag": ("1", str, "The name of the event. Should be numeric for "
                  "now."),
    "is_dissipative": (True, bool, "Dissipative simulation or not"),
    "stf_header": ([
        "STF written by the wfs_input_generator",
        "    https://github.com/krischer/wfs_input_generator",
        "The original source of the STF is not known to the",
        "input generator module."],
        lambda x: map(str, x),
        "The header of the STF function. It serves no purpose but can be "
        "used to store information about the STF in the first four lines. It "
        "is a list with up to four entries."),
    "output_displacement": (False, bool, "Output the displacement field"),
    "displacement_snapshot_sampling": (
        10000, int, "Sampling rate of output displacement field"),
    "lagrange_polynomial_degree": (
        4, int, "Degree of the Lagrange Polynomials"),
    "simulation_type": (
        "normal simulation", str, "The type of simulation to "
        "perform. One of 'normal simulation', 'adjoint forward', "
        "'adjoint backward'"),
    "adjoint_forward_sampling_rate": (
        15, int, "The sampling rate of the adjoint forward field for an "
        "adjoint simulation run"),
    "adjoint_forward_wavefield_output_folder": (
        "", str, "The output folder of the adjoint forward field if "
        "requested. If empty, it will be set to a subfolder of the the output "
        "directory."),
    "rotation_angle_in_degree": (
        0.0, float, "A possible rotation of the mesh. All data will be "
        "rotated in the opposite way. Useful for simulation close to the "
        "equator."),
    "rotation_axis": (
        [0.0, 0.0, 1.0], lambda x: map(float, x),
        "The rotation angle given as [x, y, z] in correspondance with the "
        "SES3D coordinate system."),
    "Q_model_relaxation_times": (
        [1.7308, 14.3961, 22.9973],
        lambda x: map(float, x),
        "The relaxations times for the different Q model mechanisms"),
    "Q_model_weights_of_relaxation_mechanisms": (
        [2.5100, 2.4354, 0.0879],
        lambda x: map(float, x),
        "The weights for relaxations mechanisms for the Q model mechanisms")
}


def write(config, events, stations):
    """
    Writes input files for SES3D version 4.0.

    Can only simulate one event at a time. If more events are present, an error
    will be raised.
    """
    if len(config.stf_header) > 4:
        msg = "The STF header can only be up to 4 lines."
        raise ValueError(msg)
    # ========================================================================
    # preliminaries
    # ========================================================================

    if not config.adjoint_forward_wavefield_output_folder:
        config.adjoint_forward_wavefield_output_folder = \
            os.path.join(config.output_folder, "ADJOINT_FORWARD_FIELD")

    output_files = {}

    # The data needs to be rotated in the opposite direction.
    if config.rotation_angle_in_degree:
        config.rotation_angle_in_degree *= -1.0

    # Map and assert the simulation type.
    sim_map = {"normal simulation": 0, "adjoint forward": 1,
               "adjoint reverse": 2}

    if config.simulation_type not in sim_map:
        msg = "simulation_type needs to be on of %s." % \
            ", ".join(sim_map.keys())
        raise ValueError(msg)

    simulation_type = sim_map[config.simulation_type]

    # Only exactly one event is acceptable.
    if len(events) != 1:
        msg = "Exactly one event is required for SES3D 4.0."
        raise ValueError(msg)
    event = events[0]

    # ========================================================================
    # setup file
    # =========================================================================

    # Assemble the mesh to have everything in one place
    mesh = obspy.core.AttribDict()
    mesh.min_latitude = config.mesh_min_latitude
    mesh.max_latitude = config.mesh_max_latitude
    mesh.min_longitude = config.mesh_min_longitude
    mesh.max_longitude = config.mesh_max_longitude
    mesh.min_depth_in_km = config.mesh_min_depth_in_km
    mesh.max_depth_in_km = config.mesh_max_depth_in_km

    # Rotate coordinates and moment tensor if requested.
    if config.rotation_angle_in_degree:
        lat, lng = rotations.rotate_lat_lon(
            event["latitude"],
            event["longitude"], config.rotation_axis,
            config.rotation_angle_in_degree)
        m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = rotations.rotate_moment_tensor(
            event["m_rr"], event["m_tt"], event["m_pp"], event["m_rt"],
            event["m_rp"], event["m_tp"], event["latitude"],
            event["longitude"], config.rotation_axis,
            config.rotation_angle_in_degree)
    else:
        lat, lng = (event["latitude"], event["longitude"])
        m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = (
            event["m_rr"], event["m_tt"], event["m_pp"], event["m_rt"],
            event["m_rp"], event["m_tp"])

    # Check if the event still lies within bounds. Otherwise the whole
    # simulation does not make much sense.
    if _is_in_bounds(lat, lng, mesh) is False:
        msg = "Event is not in the domain!"
        raise ValueError(msg)

    setup_file_template = (
        "MODEL ==============================================================="
        "================================================================="
        "=====\n"
        "{theta_min:<44.6f}! theta_min (colatitude) in degrees\n"
        "{theta_max:<44.6f}! theta_max (colatitude) in degrees\n"
        "{phi_min:<44.6f}! phi_min (longitude) in degrees\n"
        "{phi_max:<44.6f}! phi_max (longitude) in degrees\n"
        "{z_min:<44.6f}! z_min (radius) in m\n"
        "{z_max:<44.6f}! z_max (radius) in m\n"
        "{is_diss:<44d}! is_diss\n"
        "{model_type:<44d}! model_type\n"
        "COMPUTATIONAL SETUP (PARALLELISATION) ==============================="
        "================================================================="
        "=====\n"
        "{nx_global:<44d}! nx_global, "
        "(nx_global+px = global # elements in theta direction)\n"
        "{ny_global:<44d}! ny_global, "
        "(ny_global+py = global # elements in phi direction)\n"
        "{nz_global:<44d}! nz_global, "
        "(nz_global+pz = global # of elements in r direction)\n"
        "{lpd:<44d}! lpd, LAGRANGE polynomial degree\n"
        "{px:<44d}! px, processors in theta direction\n"
        "{py:<44d}! py, processors in phi direction\n"
        "{pz:<44d}! pz, processors in r direction\n"
        "ADJOINT PARAMETERS =================================================="
        "================================================================="
        "=====\n"
        "{adjoint_flag:<44d}! adjoint_flag (0=normal simulation, "
        "1=adjoint forward, 2=adjoint reverse)\n"
        "{samp_ad:<44d}! samp_ad, sampling rate of forward field\n"
        "{adjoint_wavefield_folder}")

    setup_file = setup_file_template.format(
        # Colatitude! Swaps min and max.
        theta_min=rotations.lat2colat(float(mesh.max_latitude)),
        theta_max=rotations.lat2colat(float(mesh.min_latitude)),
        phi_min=float(mesh.min_longitude),
        phi_max=float(mesh.max_longitude),
        # Min/max radius and depth are inverse to each other.
        z_min=EARTH_RADIUS - (float(mesh.max_depth_in_km) * 1000.0),
        z_max=EARTH_RADIUS - (float(mesh.min_depth_in_km) * 1000.0),
        is_diss=1 if config.is_dissipative else 0,
        model_type=1,
        lpd=int(config.lagrange_polynomial_degree),
        # Computation setup.
        nx_global=config.nx_global,
        ny_global=config.ny_global,
        nz_global=config.nz_global,
        px=config.px,
        py=config.py,
        pz=config.pz,
        adjoint_flag=simulation_type,
        samp_ad=config.adjoint_forward_sampling_rate,
        adjoint_wavefield_folder=config
        .adjoint_forward_wavefield_output_folder)

    output_files["setup"] = setup_file

    # =========================================================================
    # event file
    # =========================================================================

    event_template = (
        "SIMULATION PARAMETERS ==============================================="
        "===================================\n"
        "{nt:<44d}! nt, number of time steps\n"
        "{dt:<44.6f}! dt in sec, time increment\n"
        "SOURCE =============================================================="
        "===================================\n"
        "{xxs:<44.6f}! xxs, theta-coord. center of source in degrees\n"
        "{yys:<44.6f}! yys, phi-coord. center of source in degrees\n"
        "{zzs:<44.6f}! zzs, source depth in (m)\n"
        "{srctype:<44d}! srctype, 1:f_x, 2:f_y, 3:f_z, 10:M_ij\n"
        "{m_tt:<44.6e}! M_theta_theta\n"
        "{m_pp:<44.6e}! M_phi_phi\n"
        "{m_rr:<44.6e}! M_r_r\n"
        "{m_tp:<44.6e}! M_theta_phi\n"
        "{m_tr:<44.6e}! M_theta_r\n"
        "{m_pr:<44.6e}! M_phi_r\n"
        "OUTPUT DIRECTORY ===================================================="
        "==================================\n"
        "{output_folder}\n"
        "OUTPUT FLAGS ========================================================"
        "==================================\n"
        "{ssamp:<44d}! ssamp, snapshot sampling\n"
        "{output_displacement:<44d}! output_displacement, output displacement "
        "field (1=yes,0=no)")

    event_file = event_template.format(
        nt=int(config.number_of_time_steps),
        dt=float(config.time_increment_in_s),
        # Colatitude!
        xxs=rotations.lat2colat(float(lat)),
        yys=float(lng),
        zzs=float(event["depth_in_km"] * 1000.0),
        srctype=10,
        m_tt=float(m_tt),
        m_pp=float(m_pp),
        m_rr=float(m_rr),
        m_tp=float(m_tp),
        m_tr=float(m_rt),
        m_pr=float(m_rp),
        output_folder=config.output_folder,
        ssamp=int(config.displacement_snapshot_sampling),
        output_displacement=1 if config.output_displacement else 0)

    # Put it in the collected dictionary.
    fn = "event_%s" % config.event_tag
    output_files[fn] = event_file

    # =========================================================================
    # event_list
    # =========================================================================

    # Make the event_list. Currently, only one event is used
    output_files["event_list"] = "{0:<44d}! n_events = number of events\n{1}"\
        .format(1, config.event_tag)

    # =========================================================================
    # recfile
    # =========================================================================

    recfile_parts = []
    for station in stations:
        # Also rotate each station if desired.
        if config.rotation_angle_in_degree:
            lat, lng = rotations.rotate_lat_lon(
                station["latitude"], station["longitude"],
                config.rotation_axis, config.rotation_angle_in_degree)
        else:
            lat, lng = (station["latitude"], station["longitude"])

        # Check if the stations still lies within bounds of the mesh.
        if not _is_in_bounds(lat, lng, mesh):
            msg = "Stations %s is not in the domain. Will be skipped." % \
                station["id"]
            print msg
            continue

        depth = -1.0 * (station["elevation_in_m"] -
                        station["local_depth_in_m"])
        if depth < 0:
            depth = 0.0
        recfile_parts.append("{network:_<2s}.{station:_<5s}.___".format(
            network=station["id"].split(".")[0],
            station=station["id"].split(".")[1]))
        recfile_parts.append(
            "{colatitude:.6f} {longitude:.6f} {depth:.1f}"
            .format(colatitude=rotations.lat2colat(float(lat)),
                    longitude=float(lng), depth=float(depth)))
    recfile_parts.insert(0, "%i" % (len(recfile_parts) // 2))

    # Put it in the collected dictionary
    fn = "recfile_" + config.event_tag
    output_files[fn] = "\n".join(recfile_parts)

    # =========================================================================
    # relaxation parameters
    # =========================================================================
    # Write the relaxation file.
    relax_file = (
        "RELAXATION TIMES [s] =====================\n"
        "{relax_times}\n"
        "WEIGHTS OF RELAXATION MECHANISMS =========\n"
        "{relax_weights}").format(
        relax_times="\n".join(["%.6f" % _i for _i in
                               config.Q_model_relaxation_times]),
        relax_weights="\n".join([
            "%.6f" % _i for _i in
            config.Q_model_weights_of_relaxation_mechanisms]))

    output_files["relax"] = relax_file

    # =========================================================================
    # source-time function
    # =========================================================================
    # Also write the source time function.
    stf = []
    for line in config.stf_header:
        stf.append("# " + line.strip().replace("\n", " "))
    # Fill remaining lines.
    while len(stf) < 4:
        stf.append("#")
    stf.extend("%e" % _i for _i in config.source_time_function)

    output_files["stf"] = "\n".join(stf)

    # =========================================================================
    # finalize
    # =========================================================================
    # Make sure all output files have an empty new line at the end.
    for key in output_files.iterkeys():
        output_files[key] += "\n\n"

    return output_files


def _is_in_bounds(lat, lng, mesh):
    if (mesh.min_latitude <= lat <= mesh.max_latitude) and \
       (mesh.min_longitude <= lng <= mesh.max_longitude):
        return True
    return False
