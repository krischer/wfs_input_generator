#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file writer for SPECFEM3D_CARTESIAN.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
    Emanuele Casarotti (emanuele.casarotti@ingv.it), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import numpy as np
import obspy
import os



# Define the required configuration items. The key is always the name of the
# configuration item and the value is a tuple. The first item in the tuple is
# the function or type that it will be converted to and the second is the
# documentation.
REQUIRED_CONFIGURATION = {
    "NPROC":(4,int,"number of MPI processors"),
    "NSTEP":(1000,int"The number of time steps"),
    "DT":(0.05,float,"The time increment in seconds"),
    "SIMULATION_TYPE": (1,int,"forward or adjoint simulation, 1 = forward, 2 = adjoint, 3 = both simultaneously")
}

# The default configuration item. Contains everything that can sensibly be set
# to some default value. The syntax is very similar to the
# REQUIRED_CONFIGURATION except that the tuple now has three items, the first
# one being the actual default value.
DEFAULT_CONFIGURATION = {
    "SIMULATION_TYPE": (1,int,"forward or adjoint simulation, 1 = forward, 2 = adjoint, 3 = both simultaneously"),
    "NOISE_TOMOGRAPHY": (0,int,"noise tomography simulation, 0 = earthquake simulation,  1/2/3 = three steps in noise simulation"),
    "SAVE_FORWARD":('.false.',str,"save forward wavefield"),
    "UTM_PROJECTION_ZONE":(11,int,'set up the utm zone, if SUPPRESS_UTM_PROJECTION is false'),
    "SUPPRESS_UTM_PROJECTION":('.true.',str,"suppress the utm projection"),
    "NPROC":(4,int,"number of MPI processors"),
    "NSTEP":(1000,int"The number of time steps"),
    "DT":(0.05,float,"The time increment in seconds"),
    "NGNOD":(8,int,"number of nodes for 2D and 3D shape functions for hexahedral,we use either 8-node mesh elements (bricks) or 27-node elements.If you use our internal mesher, the only option is 8-node bricks (27-node elements are not supported)"),
    "MODEL": ('default',str,"setup the geological models, options are: default (model parameters described by mesh properties), 1d_prem,1d_socal,1d_cascadia,aniso,external,gll,salton_trough,tomo"),
    "APPROXIMATE_(OCEAN_LOAD":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "TOPOGRAPHY":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "ATTENUATION":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "FULL_ATTENUATION_SOLID":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "ANISOTROPY":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "GRAVITY":('.false.',str,"see SPECFEM3D_CARTESIAN manual"),
    "TOMOGRAPHY_PATH":("../DATA/tomo_files/",str,"path for external tomographic models files"),
    "USE_OLSEN_ATTENUATION":('.false.',str,"use the Olsen attenuation, Q_mu = constant * v_s attenuation rule"),
    "OLSEN_ATTENUATION_RATIO":(0.05,float,"Olsen's constant for Q_mu = constant * v_s attenuation rule"),
    "PML_CONDITIONS":('.false.',str,"C-PML boundary conditions for a regional simulation"),
    "PML_INSTEAD_OF_FREE_SURFACE":('.false.',str,"C-PML boundary conditions instead of free surface on the top"),
    "f0_FOR_PML":(12.7,float,"C-PML dominant frequency,see manual"),
    "STACEY_ABSORBING_CONDITIONS":(".false.",str,"Stacey absorbing boundary conditions for a regional simulation"),
    "STACEY_INSTEAD_OF_FREE_SURFACE":(".false.",str,"Stacey absorbing top surface (defined in mesh as 'free_surface_file')")  = .false.
    "CREATE_SHAKEMAP"        :(".false.",str,"save shakemap files"),
    "MOVIE_SURFACE"          :(".false.",str,"save velocity snapshot files only for surfaces"),
    "MOVIE_TYPE"             :(1,int,"")        ,
    "MOVIE_VOLUME"           :(".false.",str,"save the entire volumetric velocity snapshot files "),
    "SAVE_DISPLACEMENT"      :(".false.",str,"save displacement instead velocity in the snapshot files"),
    "USE_HIGHRES_FOR_MOVIES" :(".false.",str,"save high resolution snapshot files (all GLL points)"),
    "NTSTEP_BETWEEN_FRAMES"  :(200,int,"number of timesteps between 2 consecutive snapshots")      ,
    "HDUR_MOVIE"             :(0.0,float,"half duration for snapshot files")    ,
    "SAVE_MESH_FILES"             :(".false.",str,"save VTK mesh files to check the mesh"),
    "LOCAL_PATH":("../OUTPUT_FILES/DATABASES_MPI",str,"path to store the local database file on each node"),
    "NTSTEP_BETWEEN_OUTPUT_INFO"  :(500,int,"interval at which we output time step info and max of norm of displacement")      ,
    "NTSTEP_BETWEEN_OUTPUT_SEISMOS"  :(10000,int,"interval in time steps for writing of seismograms")      ,
    "NTSTEP_BETWEEN_READ_ADJSRC"  :(0,int,"interval in time steps for reading adjoint traces,0 = read the whole adjoint sources at the same time"),
    "USE_FORCE_POINT_SOURCE"             :(".false.",str,"# use a (tilted) FORCESOLUTION force point source (or several) instead of a CMTSOLUTION moment-tensor source. If this flag is turned on, the FORCESOLUTION file must be edited by precising:\n- the corresponding time-shift parameter,\n - the half duration parameter of the source,\n - the coordinates of the source,\n - the magnitude of the force source,\n - the components of a (non-unitary) direction vector for the force source in the E/N/Z_UP basis.\n The direction vector is made unitary internally in the code and thus only its direction matters here;\n its norm is ignored and the norm of the force used is the factor force source times the source time function."),
    "USE_RICKER_TIME_FUNCTION"             :(".false.",str,"set to true to use a Ricker source time function instead of the source time functions set by default to represent a (tilted) FORCESOLUTION force point source or a CMTSOLUTION moment-tensor source."),
    "GPU_MODE"             :(".false.",str,"set .true. for GPU support")
}


def write(config, events, stations):
    """
    Writes input files for SPECFEM3D_CARTESIAN.

    Can only simulate one event at a time. If finite fault is present, an error
    will be raised.
    """
    class fbool:
        """ 
        Fortran bool
        """
        def bl(self,var):
            if var:
                return '.true.'
            else:
                return '.false.'
            
        
        
    
    fortran=fbool()
    
    CMT_SOLUTION_template=(        
        "PDE  {time_year} {time_month} {time_day} {time_hh} {time_mm} {time_ss}  {event_latitude} {event_longitude} {event_depth} {event_mag} {event_mag} {event_name}\n"
        "event name:       {event_name}\n"
        "time shift:       {time_shift}\n"
        "half duration:    {half_duration}\n"
        "latitude:       {event_latitude}\n"
        "longitude:      {event_longitude}\n"
        "depth:            {event_depth}\n"
        "Mrr:       {mrr}\n"
        "Mtt:       {mtt}\n"
        "Mpp:       {mpp}\n"
        "Mrt:       {mrt}\n"
        "Mrp:       {mrp}\n"
        "Mtp:       {mtp}")
    
    setup_file_template = (
        "# simulation input parameters\n",
        "#\n",
        "# forward or adjoint simulation\n",
        "# 1 = forward, 2 = adjoint, 3 = both simultaneously\n",
        "SIMULATION_TYPE                 = {SIMULATION_TYPE}\n",
        "# 0 = earthquake simulation,  1/2/3 = three steps in noise simulation\n",
        "NOISE_TOMOGRAPHY                = {NOISE_TOMOGRAPHY}\n",
        "SAVE_FORWARD                    = {SAVE_FORWARD}\n",
        "\n",
        "# UTM projection parameters\n",
        "UTM_PROJECTION_ZONE             = {UTM_PROJECTION_ZONE}\n",
        "SUPPRESS_UTM_PROJECTION         = {SUPPRESS_UTM_PROJECTION}\n",
        "\n",
        "# number of MPI processors\n\n",
        "NPROC                           = {NPROC}\n",
        "\n"
        "# time step parameters\n",
        "NSTEP                           = {NSTEP}\n",
        "DT                              = {DT}\n",
        "\n",
        "# number of nodes for 2D and 3D shape functions for hexahedra\n",
        "# we use either 8-node mesh elements (bricks) or 27-node elements.\n",
        "# If you use our internal mesher, the only option is 8-node bricks (27-node elements are not supported)\n",
        "# CUBIT does not support HEX27 elements either (it can generate them, but they are flat, i.e. identical to HEX8).\n",
        "# To generate HEX27 elements with curvature properly taken into account, you can use Gmsh http://geuz.org/gmsh/\n",
        "NGNOD                       = {NGNOD}\n",
        "\n",
        "# models:\n",
        "# available options are:\n",
        "#   default (model parameters described by mesh properties)\n",
        "# 1D models available are:\n",
        "#   1d_prem,1d_socal,1d_cascadia\n",
        "# 3D models available are:\n",
        "#   aniso,external,gll,salton_trough,tomo\n",
        "MODEL                           = {MODEL}\n",
        "\n",
        "# parameters describing the model\n",
        "APPROXIMATE_OCEAN_LOAD          = {APPROXIMATE_OCEAN_LOAD}\n",
        "TOPOGRAPHY                      = {TOPOGRAPHY}\n",
        "ATTENUATION                     = {ATTENUATION}\n",
        "FULL_ATTENUATION_SOLID          = {FULL_ATTENUATION_SOLID}\n",
        "ANISOTROPY                      = {ANISOTROPY}\n",
        "GRAVITY                         = {GRAVITY}\n",
        "\n",
        "# path for external tomographic models files\n",
        "TOMOGRAPHY_PATH                 = {TOMOGRAPHY_PATH}\n",
        "\n",
        "# Olsen's constant for Q_mu = constant * v_s attenuation rule\n",
        "USE_OLSEN_ATTENUATION           = {USE_OLSEN_ATTENUATION}\n",
        "OLSEN_ATTENUATION_RATIO         = {OLSEN_ATTENUATION_RATIO}\n",
        "\n",
        "# C-PML boundary conditions for a regional simulation\n",
        "PML_CONDITIONS                  = {PML_CONDITIONS}\n",
        "\n",
        "# C-PML top surface\n",
        "PML_INSTEAD_OF_FREE_SURFACE     = {PML_INSTEAD_OF_FREE_SURFACE}\n",
        "\n",
        "# C-PML dominant frequency\n",
        "f0_FOR_PML                      = {f0_FOR_PML}\n",
        "\n",
        "# parameters used to rotate C-PML boundary conditions by a given angle (not implemented yet)\n",
        "# ROTATE_PML_ACTIVATE           = {ROTATE_PML_ACTIVATE}\n",
        "# ROTATE_PML_ANGLE              = {ROTATE_PML_ANGLE}\n",
        "\n",
        "# Stacey absorbing boundary conditions for a regional simulation (obsolete, using CPML above is much better)\n",
        "STACEY_ABSORBING_CONDITIONS     = {STACEY_ABSORBING_CONDITIONS}\n",
        "\n",
        "# Stacey absorbing top surface (defined in mesh as 'free_surface_file') (obsolete, using CPML above is much better)\n",
        "STACEY_INSTEAD_OF_FREE_SURFACE  = {STACEY_INSTEAD_OF_FREE_SURFACE}\n",
        "\n",
        "# save AVS or OpenDX movies\n",
        "# MOVIE_TYPE = 1 to show the top surface\n",
        "# MOVIE_TYPE = 2 to show all the external faces of the mesh\n",
        "CREATE_SHAKEMAP                 = {CREATE_SHAKEMAP}\n",
        "MOVIE_SURFACE                   = {MOVIE_SURFACE}\n",
        "MOVIE_TYPE                      = {MOVIE_TYPE}\n",
        "MOVIE_VOLUME                    = {MOVIE_VOLUME}\n",
        "SAVE_DISPLACEMENT               = {SAVE_DISPLACEMENT}\n",
        "USE_HIGHRES_FOR_MOVIES          = {USE_HIGHRES_FOR_MOVIES}\n",
        "NTSTEP_BETWEEN_FRAMES           = {NTSTEP_BETWEEN_FRAMES}\n",
        "HDUR_MOVIE                      = {HDUR_MOVIE}\n",
        "\n",
        "# save AVS or OpenDX mesh files to check the mesh\n",
        "SAVE_MESH_FILES                 = {SAVE_MESH_FILES}\n",
        "\n",
        "# path to store the local database file on each node\n",
        "LOCAL_PATH                      = {LOCAL_PATH}\n",
        "
        "# interval at which we output time step info and max of norm of displacement\n",
        "NTSTEP_BETWEEN_OUTPUT_INFO      = {NTSTEP_BETWEEN_OUTPUT_INFO}\n",
        "\n",
        "# interval in time steps for writing of seismograms\n",
        "NTSTEP_BETWEEN_OUTPUT_SEISMOS   = {NTSTEP_BETWEEN_OUTPUT_SEISMOS}\n",
        "\n",
        "# interval in time steps for reading adjoint traces\n",
        "# 0 = read the whole adjoint sources at the same time\n",
        "NTSTEP_BETWEEN_READ_ADJSRC      = {NTSTEP_BETWEEN_READ_ADJSRC}\n",
        "\n",
        "# use a (tilted) FORCESOLUTION force point source (or several) instead of a CMTSOLUTION moment-tensor source.\n",
        "# This can be useful e.g. for oil industry foothills simulations or asteroid simulations\n",
        "# in which the source is a vertical force, normal force, inclined force, impact etc.\n",
        "# If this flag is turned on, the FORCESOLUTION file must be edited by precising:\n",
        "# - the corresponding time-shift parameter,\n",
        "# - the half duration parameter of the source,\n",
        "# - the coordinates of the source,\n",
        "# - the magnitude of the force source,\n",
        "# - the components of a (non-unitary) direction vector for the force source in the E/N/Z_UP basis.\n",
        "# The direction vector is made unitary internally in the code and thus only its direction matters here;\n",
        "# its norm is ignored and the norm of the force used is the factor force source times the source time function.\n",
        "USE_FORCE_POINT_SOURCE          = {USE_FORCE_POINT_SOURCE}\n",
        "\n",
        "# set to true to use a Ricker source time function instead of the source time functions set by default\n",
        "# to represent a (tilted) FORCESOLUTION force point source or a CMTSOLUTION moment-tensor source.\n",
        "USE_RICKER_TIME_FUNCTION        = {USE_RICKER_TIME_FUNCTION}\n",
        "\n",
        "# print source time function\n",
        "PRINT_SOURCE_TIME_FUNCTION      = {PRINT_SOURCE_TIME_FUNCTION}\n",
        "\n",
        "# set to true to use GPUs\n",
        "GPU_MODE                        = {GPU_MODE}")
    
    try:
        magnitude=float(event['magnitude'])
    else:
        magnitude=0
        
    lat, lng = (event["latitude"], event["longitude"])
    m_rr, m_tt, m_pp, m_rt, m_rp, m_tp = (event["m_rr"], event["m_tt"],
        event["m_pp"], event["m_rt"], event["m_rp"], event["m_tp"])
    
    CMT_SOLUTION_file = CMT_SOLUTION_template.format(
        time_year=float(event["origin_time"].year),
        time_month=float(event["origin_time"].month),
        time_day=float(event["origin_time"].day),
        time_hh=float(event["origin_time"].hh),
        time_mm=float(event["origin_time"].mm),
        time_ss=float(event["origin_time"].ss),
        event_mag=magnitude,
        event_name=event["origin_time"].strptime()+str(magnitude),
        event_latitude=float(lat),
        event_longitude=float(lng),
        event_depth=float(event["depth_in_km"]),
        half_duration=0,
        time_shift=0,
        mtt=float(m_tt),
        mpp=float(m_pp),
        mrr=float(m_rr),
        mtp=float(m_tp),
        mrt=float(m_rt),
        mrp=float(m_rp)
        )
    
    setup_file = setup_file_template.format()
    
    recfile_parts = []
    for station in stations:
        recfile_parts.append("{station:_<5s} {network:_<2s} {latitude:.10f} {longitude:.10f} {elev:.1f} {buried:.1f}".format(
            network=station["network"],
            station=station["id"],
            latitude=float(station["latitude"]),
            longitude=float(station["longitude"]),
            elev=float(station["elevation_in_m"]),
            buried=float(station["local_depth_in_m"])
            ))
    recfile_parts.insert(0, "%i" % (len(recfile_parts) // 2))
    
    
           
    output_files = {}

    # Put it in the collected dictionary.
    output_files["event_1"] = CMT_SOLUTION_file
    output_files["event_list"] = \
        "{0:<44d}! n_events = number of events\n{0}".format(1)


    output_files["recfile"] = "\n".join(recfile_parts)

    output_files["setup"] = setup_file

    # Make sure all output files have an empty new line at the end.
    for key in output_files.iterkeys():
        output_files[key] += "\n"

    return output_files
