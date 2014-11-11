#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file writer for SPECFEM3D_CARTESIAN.

:copyright:
    Emanuele Casarotti (emanuele.casarotti@ingv.it), 2013
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import copy
import math

# Define the required configuration items. The key is always the name of the
# configuration item and the value is a tuple. The first item in the tuple is
# the function or type that it will be converted to and the second is the
# documentation.
REQUIRED_CONFIGURATION = {
    "NPROC": (int, "number of MPI processors"),
    "NSTEP": (int, "The number of time steps"),
    "DT": (float, "The time increment in seconds"),
    "SIMULATION_TYPE": (
        int, "forward or adjoint simulation, 1 = forward, "
        "2 = adjoint, 3 = both simultaneously")
}

# The default configuration item. Contains everything that can sensibly be set
# to some default value. The syntax is very similar to the
# REQUIRED_CONFIGURATION except that the tuple now has three items, the first
# one being the actual default value.
DEFAULT_CONFIGURATION = {
    "NOISE_TOMOGRAPHY": (
        0, int, "noise tomography simulation, "
        "0 = earthquake simulation,  1/2/3 = three steps in noise simulation"),
    "SAVE_FORWARD": (False, bool, "save forward wavefield"),
    "UTM_PROJECTION_ZONE": (
        11, int,
        "set up the utm zone, if SUPPRESS_UTM_PROJECTION is false"),
    "SUPPRESS_UTM_PROJECTION": (True, bool, "suppress the utm projection"),
    "NGNOD": (
        8, int, "number of nodes for 2D and 3D shape functions for "
        "hexahedral,we use either 8-node mesh elements (bricks) or 27-node "
        "elements.If you use our internal mesher, the only option is 8-node "
        "bricks (27-node elements are not supported)"),
    "MODEL": (
        "default", str, "setup the geological models, options are: "
        "default (model parameters described by mesh properties), 1d_prem,"
        "1d_socal,1d_cascadia,aniso,external,gll,salton_trough,tomo"),
    "SEP_MODEL_DIRECTORY": (
        "./DATA/my_SEP_model/", str, "SEP model folder if you are using one"),
    "APPROXIMATE_OCEAN_LOAD": (
        False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "TOPOGRAPHY": (False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "ATTENUATION": (False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "FULL_ATTENUATION_SOLID": (
        False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "ANISOTROPY": (False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "GRAVITY": (False, bool, "see SPECFEM3D_CARTESIAN manual"),
    "TOMOGRAPHY_PATH": ("../DATA/tomo_files/", str,
                        "path for external tomographic models files"),
    "USE_OLSEN_ATTENUATION": (
        False, bool,
        "use the Olsen attenuation, Q_mu = constant * v_s attenuation rule"),
    "OLSEN_ATTENUATION_RATIO": (
        0.05, float,
        "Olsen's constant for Q_mu = constant * v_s attenuation rule"),
    "PML_CONDITIONS": (
        False, bool,
        "C-PML boundary conditions for a regional simulation"),
    "PML_INSTEAD_OF_FREE_SURFACE": (
        False, bool,
        "C-PML boundary conditions instead of free surface on the top"),
    "f0_FOR_PML": (12.7, float, "C-PML dominant frequency,see manual"),
    "STACEY_ABSORBING_CONDITIONS": (
        False, bool,
        "Stacey absorbing boundary conditions for a regional simulation"),
    "STACEY_INSTEAD_OF_FREE_SURFACE": (
        False, bool, "Stacey absorbing top "
        "surface (defined in mesh as 'free_surface_file')"),
    "CREATE_SHAKEMAP": (False, bool, "save shakemap files"),
    "MOVIE_SURFACE": (
        False, bool,
        "save velocity snapshot files only for surfaces"),
    "MOVIE_TYPE": (1, int, ""),
    "MOVIE_VOLUME": (
        False, bool,
        "save the entire volumetric velocity snapshot files "),
    "SAVE_DISPLACEMENT": (
        False, bool,
        "save displacement instead velocity in the snapshot files"),
    "USE_HIGHRES_FOR_MOVIES": (
        False, bool,
        "save high resolution snapshot files (all GLL points)"),
    "NTSTEP_BETWEEN_FRAMES": (
        200, int,
        "number of timesteps between 2 consecutive snapshots"),
    "HDUR_MOVIE": (0.0, float,
                   "half duration for snapshot files"),
    "SAVE_MESH_FILES": (
        False, bool,
        "save VTK mesh files to check the mesh"),
    "LOCAL_PATH": (
        "../OUTPUT_FILES/DATABASES_MPI", str,
        "path to store the local database file on each node"),
    "NTSTEP_BETWEEN_OUTPUT_INFO": (
        500, int, "interval at which we output "
        "time step info and max of norm of displacement"),
    "NTSTEP_BETWEEN_OUTPUT_SEISMOS": (
        10000, int,
        "interval in time steps for writing of seismograms"),
    "NTSTEP_BETWEEN_READ_ADJSRC": (
        0, int, "interval in time steps for "
        "reading adjoint traces,0 = read the whole adjoint sources at the "
        "same time"),
    "USE_FORCE_POINT_SOURCE": (
        False, bool, "# use a (tilted) "
        "FORCESOLUTION force point source (or several) instead of a "
        "CMTSOLUTION moment-tensor source. If this flag is turned on, "
        "the FORCESOLUTION file must be edited by precising:\n- the "
        "corresponding time-shift parameter,\n - the half duration parameter "
        "of the source,\n - the coordinates of the source,\n - the magnitude "
        "of the force source,\n - the components of a (non-unitary) direction "
        "vector for the force source in the E/N/Z_UP basis.\n The direction "
        "vector is made unitary internally in the code and thus only its "
        "direction matters here;\n its norm is ignored and the norm of the "
        "force used is the factor force source times the source time "
        "function."),
    "USE_RICKER_TIME_FUNCTION": (
        False, bool, "set to true to use a Ricker "
        "source time function instead of the source time functions set by "
        "default to represent a (tilted) FORCESOLUTION force point source or "
        "a CMTSOLUTION moment-tensor source."),
    "GPU_MODE": (False, bool, "set .true. for GPU support"),
    "ROTATE_PML_ACTIVATE": (False, bool, ""),
    "ROTATE_PML_ANGLE": (0.0, float, ""),
    "PRINT_SOURCE_TIME_FUNCTION": (False, bool, ""),
    "COUPLE_WITH_EXTERNAL_CODE": (False, bool, ""),
    "EXTERNAL_CODE_TYPE": (1, int, "1 = DSM, 2 = AxiSEM, 3 = FK"),
    "TRACTION_PATH": ("./DATA/DSM_tractions_for_specfem3D/", str, ""),
    "MESH_A_CHUNK_OF_THE_EARTH": (True, bool, ""),
    "ADIOS_ENABLED": (False, bool, ""),
    "ADIOS_FOR_DATABASES": (False, bool, ""),
    "ADIOS_FOR_MESH": (False, bool, ""),
    "ADIOS_FOR_FORWARD_ARRAYS": (False, bool, ""),
    "ADIOS_FOR_KERNELS": (False, bool, ""),
}


def write(config, events, stations):
    """
    Writes input files for SPECFEM3D_CARTESIAN.

    Can only simulate one event at a time. If finite fault is present, an error
    will be raised.
    """
    def fbool(value):
        """
        Convert a value to a FORTRAN boolean representation.
        """
        if not isinstance(value, bool):
            raise TypeError
        if value:
            return ".true."
        else:
            return ".false."

    par_file_template = (
        "# simulation input parameters\n"
        "#\n"
        "# forward or adjoint simulation\n"
        "# 1 = forward, 2 = adjoint, 3 = both simultaneously\n"
        "SIMULATION_TYPE                 = {SIMULATION_TYPE}\n"
        "# 0 = earthquake simulation,  1/2/3 = "
        "three steps in noise simulation\n"
        "NOISE_TOMOGRAPHY                = {NOISE_TOMOGRAPHY}\n"
        "SAVE_FORWARD                    = {SAVE_FORWARD}\n"
        "\n"
        "# UTM projection parameters\n"
        "# Use a negative zone number for the Southern hemisphere:\n"
        "# The Northern hemisphere corresponds to zones +1 to +60,\n"
        "# The Southern hemisphere corresponds to zones -1 to -60.\n"
        "UTM_PROJECTION_ZONE             = {UTM_PROJECTION_ZONE}\n"
        "SUPPRESS_UTM_PROJECTION         = {SUPPRESS_UTM_PROJECTION}\n"
        "\n"
        "# number of MPI processors\n"
        "NPROC                           = {NPROC}\n"
        "\n"
        "# time step parameters\n"
        "NSTEP                           = {NSTEP}\n"
        "DT                              = {DT}\n"
        "\n"
        "# number of nodes for 2D and 3D shape functions for hexahedra\n"
        "# we use either 8-node mesh elements (bricks) or 27-node elements.\n"
        "# If you use our internal mesher, the only option is 8-node bricks "
        "(27-node elements are not supported)\n"
        "# CUBIT does not support HEX27 elements either (it can generate them,"
        " but they are flat, i.e. identical to HEX8).\n"
        "# To generate HEX27 elements with curvature properly taken into "
        "account, you can use Gmsh http://geuz.org/gmsh/\n"
        "NGNOD                           = {NGNOD}\n"
        "\n"
        "# models:\n"
        "# available options are:\n"
        "#   default (model parameters described by mesh properties)\n"
        "# 1D models available are:\n"
        "#   1d_prem,1d_socal,1d_cascadia\n"
        "# 3D models available are:\n"
        "#   aniso,external,gll,salton_trough,tomo,SEP...\n"
        "MODEL                           = {MODEL}\n"
        "\n"
        "# if you are using a SEP model (oil-industry format)\n"
        "SEP_MODEL_DIRECTORY             = {SEP_MODEL_DIRECTORY}\n"
        "\n"
        "# parameters describing the model\n"
        "APPROXIMATE_OCEAN_LOAD          = {APPROXIMATE_OCEAN_LOAD}\n"
        "TOPOGRAPHY                      = {TOPOGRAPHY}\n"
        "ATTENUATION                     = {ATTENUATION}\n"
        "FULL_ATTENUATION_SOLID          = {FULL_ATTENUATION_SOLID}\n"
        "ANISOTROPY                      = {ANISOTROPY}\n"
        "GRAVITY                         = {GRAVITY}\n"
        "\n"
        "# path for external tomographic models files\n"
        "TOMOGRAPHY_PATH                 = {TOMOGRAPHY_PATH}\n"
        "\n"
        "# Olsen's constant for Q_mu = constant * v_s attenuation rule\n"
        "USE_OLSEN_ATTENUATION           = {USE_OLSEN_ATTENUATION}\n"
        "OLSEN_ATTENUATION_RATIO         = {OLSEN_ATTENUATION_RATIO}\n"
        "\n"
        "# C-PML boundary conditions for a regional simulation\n"
        "PML_CONDITIONS                  = {PML_CONDITIONS}\n"
        "\n"
        "# C-PML top surface\n"
        "PML_INSTEAD_OF_FREE_SURFACE     = {PML_INSTEAD_OF_FREE_SURFACE}\n"
        "\n"
        "# C-PML dominant frequency\n"
        "f0_FOR_PML                      = {f0_FOR_PML}\n"
        "\n"
        "# parameters used to rotate C-PML boundary conditions by a given "
        "angle (not completed yet)\n"
        "# ROTATE_PML_ACTIVATE           = {ROTATE_PML_ACTIVATE}\n"
        "# ROTATE_PML_ANGLE              = {ROTATE_PML_ANGLE}\n"
        "\n"
        "# absorbing boundary conditions for a regional simulation\n"
        "STACEY_ABSORBING_CONDITIONS     = {STACEY_ABSORBING_CONDITIONS}\n"
        "\n"
        "# absorbing top surface (defined in mesh as 'free_surface_file')\n"
        "STACEY_INSTEAD_OF_FREE_SURFACE  = {STACEY_INSTEAD_OF_FREE_SURFACE}\n"
        "\n"
        "# save AVS or OpenDX movies\n"
        "# MOVIE_TYPE = 1 to show the top surface\n"
        "# MOVIE_TYPE = 2 to show all the external faces of the mesh\n"
        "CREATE_SHAKEMAP                 = {CREATE_SHAKEMAP}\n"
        "MOVIE_SURFACE                   = {MOVIE_SURFACE}\n"
        "MOVIE_TYPE                      = {MOVIE_TYPE}\n"
        "MOVIE_VOLUME                    = {MOVIE_VOLUME}\n"
        "SAVE_DISPLACEMENT               = {SAVE_DISPLACEMENT}\n"
        "USE_HIGHRES_FOR_MOVIES          = {USE_HIGHRES_FOR_MOVIES}\n"
        "NTSTEP_BETWEEN_FRAMES           = {NTSTEP_BETWEEN_FRAMES}\n"
        "HDUR_MOVIE                      = {HDUR_MOVIE}\n"
        "\n"
        "# save AVS or OpenDX mesh files to check the mesh\n"
        "SAVE_MESH_FILES                 = {SAVE_MESH_FILES}\n"
        "\n"
        "# path to store the local database file on each node\n"
        "LOCAL_PATH                      = {LOCAL_PATH}\n\n"

        "# interval at which we output time step info and max of norm of "
        "displacement\n"
        "NTSTEP_BETWEEN_OUTPUT_INFO      = {NTSTEP_BETWEEN_OUTPUT_INFO}\n"
        "\n"
        "# interval in time steps for writing of seismograms\n"
        "NTSTEP_BETWEEN_OUTPUT_SEISMOS   = {NTSTEP_BETWEEN_OUTPUT_SEISMOS}\n"
        "\n"
        "# interval in time steps for reading adjoint traces\n"
        "# 0 = read the whole adjoint sources at the same time\n"
        "NTSTEP_BETWEEN_READ_ADJSRC      = {NTSTEP_BETWEEN_READ_ADJSRC}\n"
        "\n"
        "# use a (tilted) FORCESOLUTION force point source (or several) "
        "instead of a CMTSOLUTION moment-tensor source.\n"
        "# This can be useful e.g. for oil industry foothills simulations or "
        "asteroid simulations\n"
        "# in which the source is a vertical force, normal force, inclined "
        "force, impact etc.\n"
        "# If this flag is turned on, the FORCESOLUTION file must be edited "
        "by giving:\n"
        "# - the corresponding time-shift parameter,\n"
        "# - the half duration parameter of the source,\n"
        "# - the coordinates of the source,\n"
        "# - the magnitude of the force source,\n"
        "# - the components of a direction vector for the force "
        "source in the E/N/Z_UP basis.\n"
        "# The direction vector is made unitary internally in the code and "
        "thus only its direction matters here;\n"
        "# its norm is ignored and the norm of the force used is the factor "
        "force source times the source time function.\n"
        "USE_FORCE_POINT_SOURCE          = {USE_FORCE_POINT_SOURCE}\n"
        "\n"
        "# set to true to use a Ricker source time function instead of the "
        "source time functions set by default\n"
        "# to represent a (tilted) FORCESOLUTION force point source or a "
        "CMTSOLUTION moment-tensor source.\n"
        "USE_RICKER_TIME_FUNCTION        = {USE_RICKER_TIME_FUNCTION}\n"
        "\n"
        "# print source time function\n"
        "PRINT_SOURCE_TIME_FUNCTION      = {PRINT_SOURCE_TIME_FUNCTION}\n"
        "\n"
        "# to couple with an external code (such as DSM, AxiSEM, or FK)\n"
        "COUPLE_WITH_EXTERNAL_CODE       = {COUPLE_WITH_EXTERNAL_CODE}\n"
        "EXTERNAL_CODE_TYPE              = {EXTERNAL_CODE_TYPE}"
        "   # 1 = DSM, 2 = AxiSEM, 3 = FK\n"
        "TRACTION_PATH                   = {TRACTION_PATH}\n"
        "MESH_A_CHUNK_OF_THE_EARTH       = {MESH_A_CHUNK_OF_THE_EARTH}\n"
        "\n# set to true to use GPUs\n"
        "GPU_MODE                        = {GPU_MODE}\n\n"
        "# ADIOS Options for I/Os\n"
        "ADIOS_ENABLED                   = {ADIOS_ENABLED}\n"
        "ADIOS_FOR_DATABASES             = {ADIOS_FOR_DATABASES}\n"
        "ADIOS_FOR_MESH                  = {ADIOS_FOR_MESH}\n"
        "ADIOS_FOR_FORWARD_ARRAYS        = {ADIOS_FOR_FORWARD_ARRAYS}\n"
        "ADIOS_FOR_KERNELS               = {ADIOS_FOR_KERNELS}")

    c = copy.deepcopy(config.__dict__)
    for key, value in c.items():
        if not isinstance(value, bool):
            continue
        c[key] = fbool(value)

    par_file = par_file_template.format(**c)

    # The template for the CMTSOLUTION file.
    CMT_SOLUTION_template = (
        "PDE {time_year} {time_month} {time_day} {time_hh} {time_mm} "
        "{time_ss:.2f} {event_latitude:.5f} {event_longitude:.5f} "
        "{event_depth:.5f} {event_mag:.1f} {event_mag:.1f} {event_name}\n"
        "event name:      0000000\n"
        "time shift:       0.0000\n"
        "half duration:    {half_duration:.4f}\n"
        "latitude:       {event_latitude:.5f}\n"
        "longitude:      {event_longitude:.5f}\n"
        "depth:{event_depth: 17.5f}\n"
        "Mrr:         {mrr:.6g}\n"
        "Mtt:         {mtt:.6g}\n"
        "Mpp:         {mpp:.6g}\n"
        "Mrt:         {mrt:.6g}\n"
        "Mrp:         {mrp:.6g}\n"
        "Mtp:         {mtp:.6g}")

    # Create the event file.
    if len(events) != 1:
        msg = ("The SPECFEM backend can currently only deal with a single "
               "event.")
        raise NotImplementedError(msg)
    event = events[0]

    # Calculate the moment magnitude
    M_0 = 1.0 / math.sqrt(2.0) * math.sqrt(
        event["m_rr"] ** 2 +
        event["m_tt"] ** 2 +
        event["m_pp"] ** 2)
    magnitude = 2.0 / 3.0 * math.log10(M_0) - 6.0

    lat, lng = (event["latitude"], event["longitude"])
    m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = (
        event["m_rr"], event["m_tt"], event["m_pp"], event["m_rt"],
        event["m_rp"], event["m_tp"])

    CMT_SOLUTION_file = CMT_SOLUTION_template.format(
        time_year=event["origin_time"].year,
        time_month=event["origin_time"].month,
        time_day=event["origin_time"].day,
        time_hh=event["origin_time"].hour,
        time_mm=event["origin_time"].minute,
        time_ss=event["origin_time"].second +
        event["origin_time"].microsecond / 1E6,
        event_mag=magnitude,
        event_name=str(event["origin_time"]) + "_" + ("%.1f" % magnitude),
        event_latitude=float(lat),
        event_longitude=float(lng),
        event_depth=float(event["depth_in_km"]),
        half_duration=0.0,
        # Convert to dyne * cm.
        mtt=m_tt * 1E7,
        mpp=m_pp * 1E7,
        mrr=m_rr * 1E7,
        mtp=m_tp * 1E7,
        mrt=m_rt * 1E7,
        mrp=m_rp * 1E7)

    station_parts = []
    for station in stations:
        station_parts.append(
            "{station:s} {network:s} {latitude:.5f} "
            "{longitude:.5f} {elev:.1f} {buried:.1f}".format(
                network=station["id"].split(".")[0],
                station=station["id"].split(".")[1],
                latitude=station["latitude"],
                longitude=station["longitude"],
                elev=station["elevation_in_m"],
                buried=station["local_depth_in_m"]))

    # Put the files int he output directory.
    output_files = {}
    output_files["Par_file"] = par_file
    output_files["CMTSOLUTION"] = CMT_SOLUTION_file
    output_files["STATIONS"] = "\n".join(station_parts)

    return output_files
