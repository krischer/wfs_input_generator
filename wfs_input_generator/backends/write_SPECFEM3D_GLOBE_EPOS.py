#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file writer for SPECFEM3D_CARTESIAN with support for the version the
EPOS project uses.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2017
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import inspect
import math
import os


REQUIRED_CONFIGURATION = {
    "SIMULATION_TYPE": (int, "forward or adjoint simulation; 1 = forward, "
                             "2 = adjoint, 3 = both simultaneously"),
    "NPROC": (int, "number of MPI processors"),
    "NSTEP": (int, "numer of time steps"),
    "DT": (float, "time step"),
}


DEFAULT_CONFIGURATION = {
    "NOISE_TOMOGRAPHY": (0, int, "0 = earthquake simulation,  "
                                 "1/2/3 = three steps in noise simulation"),
    "SAVE_FORWARD": (False, bool, "save forward wavefield."),

    # UTM projection parameters
    # Use a negative zone number for the Southern hemisphere:
    # The Northern hemisphere corresponds to zones +1 to +60,
    # The Southern hemisphere corresponds to zones -1 to -60.
    "UTM_PROJECTION_ZONE": (11, int, "UTM projection zone."),
    "SUPPRESS_UTM_PROJECTION": (True, bool, "Suppress UTM projection."),

    # -----------------------------------------------------------
    #
    # LDDRK time scheme
    #
    # -----------------------------------------------------------
    "USE_LDDRK": (False, bool, "Use LDDRK time scheme"),
    "INCREASE_CFL_FOR_LDDRK": (False, bool, "Increase CFL for LDDRK"),
    "RATIO_BY_WHICH_TO_INCREASE_IT": (1.4, float, "Ratio by which to "
                                                  "increase it"),
    # -----------------------------------------------------------
    #
    # Mesh
    #
    # -----------------------------------------------------------

    # number of nodes for 2D and 3D shape functions for hexahedra
    # we use either 8-node mesh elements (bricks) or 27-node elements.
    # If you use our internal mesher, the only option is 8-node bricks
    # (27-node elements are not supported)
    # CUBIT does not support HEX27 elements either (it can generate them, but
    # they are flat, i.e. identical to HEX8).
    # To generate HEX27 elements with curvature properly taken into account,
    # you can use Gmsh http://geuz.org/gmsh/
    "NGNOD": (8, int, "nodes per hex"),
    # models:
    # available options are:
    #   default (model parameters described by mesh properties)
    # 1D models available are:
    #   1d_prem,1d_socal,1d_cascadia
    # 3D models available are:
    #   aniso,external,gll,salton_trough,tomo,SEP...
    "MODEL": ("default", str, "model - 'default' will use model parameters "
                              "as described by mesh."),
    "TOMOGRAPHY_PATH": ("./DATA/tomo_files/", str,
                        "path for external tomographic models files"),
    "SEP_MODEL_DIRECTORY": ("./DATA/my_SEP_model/", str,
                            "if you are using a SEP model "
                            "(oil-industry format)"),

    # parameters describing the model
    "APPROXIMATE_OCEAN_LOAD": (False, bool, "Use ocean loading."),
    "TOPOGRAPHY": (False, bool, "Add topography."),
    "ATTENUATION": (False, bool, "Use attenuation."),
    "ANISOTROPY": (False, bool, "Use anisotropy."),
    "GRAVITY": (False, bool, "Use gravity."),

    # reference frequency for target velocity values in the velocity model
    # set here to a typical value for regional seismology / regional models
    # (dominant period of 3 seconds, i.e. frequency of 1/3 Hz)
    "ATTENUATION_f0_REFERENCE": (0.33333, float, "Reference frequency."),

    # attenuation period range over which we try to mimic a constant Q factor
    "MIN_ATTENUATION_PERIOD": (999999998.0, float, "Min attenuation period."),
    "MAX_ATTENUATION_PERIOD": (999999999.0, float, "Max attenuation period."),
    # ignore this range and ask the code to compute it automatically instead
    # based on the estimated resolution of the mesh (use this unless you
    # know what you are doing)
    "COMPUTE_FREQ_BAND_AUTOMATIC": (True, bool, "Do it fully automatically."),

    # Olsen's constant for Q_mu = constant * V_s attenuation rule
    "USE_OLSEN_ATTENUATION": (False, bool, "Use Olsen's attenuation rule."),
    "OLSEN_ATTENUATION_RATIO": (0.05, float, "Olsen's attenuation ratio."),

    # -----------------------------------------------------------
    #
    # Absorbing boundary conditions
    #
    # -----------------------------------------------------------

    # C-PML boundary conditions for a regional simulation
    # (if set to .false., and STACEY_ABSORBING_CONDITIONS is also set to
    # .false., you get a free surface instead
    # in the case of elastic or viscoelastic mesh elements, and a rigid
    # surface in the case of acoustic (fluid) elements
    "PML_CONDITIONS": (False, bool, "Use PML boundaries."),

    # C-PML top surface
    "PML_INSTEAD_OF_FREE_SURFACE": (False, bool, "Use PML also at the top."),

    # C-PML dominant frequency
    "f0_FOR_PML": (0.05555, float, "Dominant frequency for the C-PMLs."),

    # parameters used to rotate C-PML boundary conditions by a given angle
    # (not completed yet)
    # ROTATE_PML_ACTIVATE           = .false.
    # ROTATE_PML_ANGLE              = 0.

    # absorbing boundary conditions for a regional simulation
    # (if set to .false., and PML_CONDITIONS is also set to .false., you get
    # a free surface instead
    # in the case of elastic or viscoelastic mesh elements, and a rigid
    # surface in the case of acoustic (fluid) elements
    "STACEY_ABSORBING_CONDITIONS": (True, bool, "Stacey absorbing boundaries"),

    # absorbing top surface (defined in mesh as 'free_surface_file')
    "STACEY_INSTEAD_OF_FREE_SURFACE": (False, bool, "Stacey absorbing "
                                                    "boundaries also at the "
                                                    "top."),

    # When STACEY_ABSORBING_CONDITIONS is set to .true. :
    # absorbing conditions are defined in xmin, xmax, ymin, ymax and zmin
    # this option BOTTOM_FREE_SURFACE can be set to .true. to
    # make zmin free surface instead of absorbing condition
    "BOTTOM_FREE_SURFACE": (False, bool, "Free surface at the bottom."),

    # -----------------------------------------------------------
    #
    # Visualization
    #
    # -----------------------------------------------------------

    # save AVS or OpenDX movies
    "CREATE_SHAKEMAP": (False, bool, "Create a shakemap."),
    "MOVIE_SURFACE": (False, bool, "Surface movie."),
    "MOVIE_TYPE": (1, int, "MOVIE_TYPE = 1 to show the top surface "
                           "MOVIE_TYPE = 2 to show all the external faces of "
                           "the mesh"),
    "MOVIE_VOLUME": (False, bool, "Volumetric movie."),
    "SAVE_DISPLACEMENT": (False, bool, "Save the displacment."),
    "USE_HIGHRES_FOR_MOVIES": (False, bool, "Use highres for the movies."),
    "NTSTEP_BETWEEN_FRAMES": (200, int, "Timesteps between the frames."),
    "HDUR_MOVIE": (0.0, float, "Movie duration."),

    # save AVS or OpenDX mesh files to check the mesh
    "SAVE_MESH_FILES": (True, bool, "Save the mesh files to check it."),

    # path to store the local database file on each node
    "LOCAL_PATH": ("./OUTPUT_FILES/DATABASES_MPI", str, "path to local "
                                                        "database."),

    # interval at which we output time step info and max of norm of
    # displacement
    "NTSTEP_BETWEEN_OUTPUT_INFO": (500, int, "Interval at which information "
                                             "will be printed."),

    # -----------------------------------------------------------
    #
    # Sources
    #
    # -----------------------------------------------------------

    # use a (tilted) FORCESOLUTION force point source (or several) instead of
    # a CMTSOLUTION moment-tensor source.
    # This can be useful e.g. for oil industry foothills simulations or
    # asteroid simulations
    # in which the source is a vertical force, normal force, tilted force,
    # impact etc.
    # If this flag is turned on, the FORCESOLUTION file must be edited by
    # giving:
    # - the corresponding time-shift parameter,
    # - the half duration parameter of the source,
    # - the coordinates of the source,
    # - the magnitude of the force source,
    # - the components of a (non necessarily unitary) direction vector for
    # the force source in the E/N/Z_UP basis.
    # The direction vector is made unitary internally in the code and thus
    # only its direction matters here;
    # its norm is ignored and the norm of the force used is the factor force
    # source times the source time function.
    "USE_FORCE_POINT_SOURCE": (False, bool, "Use a force source."),

    # set to true to use a Ricker source time function instead of the source
    # time functions set by default
    # to represent a (tilted) FORCESOLUTION force point source or a
    # CMTSOLUTION moment-tensor source.
    "USE_RICKER_TIME_FUNCTION": (False, bool, "Use ricker source wavelet."),

    # Use an external source time function.
    # if .true. you must add a file with your source time function and the
    # file name
    # path relative to lauching directory at the end of CMTSOLUTION or
    # FORCESOURCE file
    # (with multiple sources, one file per source is required).
    # This file must have a single column containing the amplitude of the
    # source at that time step,
    # and on its first line it must contain the time step used, which must be
    # equal to DT as defined at the beginning of this Par_file (the code will
    # check that).
    # Be sure when this option is .false. to remove the name of stf file in
    # CMTSOLUTION or FORCESOURCE
    "USE_EXTERNAL_SOURCE_FILE": (False, bool, "Use an external source file."),

    # print source time function
    "PRINT_SOURCE_TIME_FUNCTION": (False, bool, "Print the source time fct."),

    # (for acoustic simulations only) determines source encoding factor +/-1
    # depending on sign of moment tensor
    # (see e.g. Krebs et al., 2009. Fast full-wavefield seismic inversion
    # using encoded sources, Geophysics, 74 (6), WCC177-WCC188.)
    "USE_SOURCE_ENCODING": (False, bool, "Use source encoding."),

    # -----------------------------------------------------------
    #
    # Seismograms
    #
    # -----------------------------------------------------------

    # interval in time steps for writing of seismograms
    "NTSTEP_BETWEEN_OUTPUT_SEISMOS": (10000, int, "Interval in time steps "
                                                  "for writing seismograms."),

    # decide if we save displacement, velocity, acceleration and/or pressure
    # in forward runs (they can be set to true simultaneously)
    # currently pressure seismograms are implemented in acoustic (i.e. fluid)
    # elements only
    "SAVE_SEISMOGRAMS_DISPLACEMENT": (True, bool, "Save displacement "
                                                  "seismograms."),
    "SAVE_SEISMOGRAMS_VELOCITY": (False, bool, "Save velocity seismograms."),
    "SAVE_SEISMOGRAMS_ACCELERATION": (False, bool, "Save acceleration "
                                                   "seismograms."),
    # currently implemented in acoustic (i.e. fluid) elements only
    "SAVE_SEISMOGRAMS_PRESSURE": (False, bool, "Save pressure seismograms."),

    # save seismograms in binary or ASCII format (binary is smaller but may
    # not be portable between machines)
    "USE_BINARY_FOR_SEISMOGRAMS": (False, bool, "Use binary output for "
                                                "seismograms."),

    # output seismograms in Seismic Unix format (binary with 240-byte-headers)
    "SU_FORMAT": (False, bool, "Use the Seismic Unix format."),

    # decide if master process writes all the seismograms or if all processes
    # do it in parallel
    "WRITE_SEISMOGRAMS_BY_MASTER": (False, bool, "Write seismograms by "
                                                 "master."),

    # save all seismograms in one large combined file instead of one file per
    # seismogram
    # to avoid overloading shared non-local file systems such as LUSTRE or
    # GPFS for instance
    "SAVE_ALL_SEISMOS_IN_ONE_FILE": (False, bool, "Save all seismograms in "
                                                  "one file."),

    # use a trick to increase accuracy of pressure seismograms in fluid
    # (acoustic) elements:
    # use the second derivative of the source for the source time function
    # instead of the source itself,
    # and then record -potential_acoustic() as pressure seismograms instead
    # of -potential_dot_dot_acoustic();
    # this is mathematically equivalent, but numerically significantly more
    # accurate because in the explicit
    # Newmark time scheme acceleration is accurate at zeroth order while
    # displacement is accurate at second order,
    # thus in fluid elements potential_dot_dot_acoustic() is accurate at
    # zeroth order while potential_acoustic()
    # is accurate at second order and thus contains significantly less
    # numerical noise.
    "USE_TRICK_FOR_BETTER_PRESSURE": (False, bool, "Increase accuracy of "
                                                   "pressure seismograms."),

    # -----------------------------------------------------------
    #
    # Energy calculation
    #
    # -----------------------------------------------------------
    # to plot energy curves, for instance to monitor how CPML absorbing layers
    # behave;
    # should be turned OFF in most cases because a bit expensive
    "OUTPUT_ENERGY": (False, bool, "Output energy."),
    # every how many time steps we compute energy (which is a bit expensive
    # to compute)
    "NTSTEP_BETWEEN_OUTPUT_ENERGY": (10, int, "Time interval at which to "
                                              "output energy."),

    # -----------------------------------------------------------
    #
    # Adjoint kernel outputs
    #
    # -----------------------------------------------------------

    # interval in time steps for reading adjoint traces
    # 0 = read the whole adjoint sources at the same time
    "NTSTEP_BETWEEN_READ_ADJSRC": (0, int, "interval in time steps for "
                                           "reading adjoint traces, 0=read "
                                           "the whole adjoint source at the "
                                           "same time"),

    # this parameter must be set to .true. to compute anisotropic kernels
    # in crust and mantle (related to the 21 Cij in geographical coordinates)
    # default is .false. to compute isotropic kernels (related to alpha and
    # beta)
    "ANISOTROPIC_KL": (False, bool, "Compute anisotropic kernels."),

    # compute transverse isotropic kernels
    # (alpha_v,alpha_h,beta_v,beta_h,eta,rho)
    # rather than fully anisotropic kernels in case ANISOTROPIC_KL is set to
    # .true.
    "SAVE_TRANSVERSE_KL": (False, bool, "Compute tranverse isotropic kernels"),

    # outputs approximate Hessian for preconditioning
    "APPROXIMATE_HESS_KL": (False, bool, "Approximate the Hessian for "
                                         "preconditioning"),

    # save Moho mesh and compute Moho boundary kernels
    "SAVE_MOHO_MESH": (False, bool, "Save the moho mesh and compute Moho "
                                    "boundary kernels"),

    # -----------------------------------------------------------

    # Dimitri Komatitsch, July 2014, CNRS Marseille, France:
    # added the ability to run several calculations (several earthquakes)
    # in an embarrassingly-parallel fashion from within the same run;
    # this can be useful when using a very large supercomputer to compute
    # many earthquakes in a catalog, in which case it can be better from
    # a batch job submission point of view to start fewer and much larger jobs,
    # each of them computing several earthquakes in parallel.
    # To turn that option on, set parameter NUMBER_OF_SIMULTANEOUS_RUNS to a
    # value greater than 1.
    # To implement that, we create NUMBER_OF_SIMULTANEOUS_RUNS MPI
    # sub-communicators,
    # each of them being labeled "my_local_mpi_comm_world", and we use them
    # in all the routines in "src/shared/parallel.f90", except in MPI_ABORT()
    # because in that case
    # we need to kill the entire run.
    # When that option is on, of course the number of processor cores used to
    # start
    # the code in the batch system must be a multiple of
    # NUMBER_OF_SIMULTANEOUS_RUNS,
    # all the individual runs must use the same number of processor cores,
    # which as usual is NPROC in the Par_file,
    # and thus the total number of processor cores to request from the batch
    # system
    # should be NUMBER_OF_SIMULTANEOUS_RUNS * NPROC.
    # All the runs to perform must be placed in directories called run0001,
    # run0002, run0003 and so on
    # (with exactly four digits).
    #
    # Imagine you have 10 independent calculations to do, each of them on 100
    # cores; you have three options:
    #
    # 1/ submit 10 jobs to the batch system
    #
    # 2/ submit a single job on 1000 cores to the batch, and in that script
    # create a sub-array of jobs to start 10 jobs,
    # each running on 100 cores (see e.g.
    # http://www.schedmd.com/slurmdocs/job_array.html )
    #
    # 3/ submit a single job on 1000 cores to the batch, start SPECFEM3D on
    # 1000 cores, create 10 sub-communicators,
    # cd into one of 10 subdirectories (called e.g. run0001, run0002,...
    # run0010) depending on the sub-communicator
    # your MPI rank belongs to, and run normally on 100 cores using that
    # sub-communicator.
    #
    # The option below implements 3/.
    #
    "NUMBER_OF_SIMULTANEOUS_RUNS": (1, int, "Number of simultaneous runs."),

    # if we perform simultaneous runs in parallel, if only the source and
    # receivers vary between these runs
    # but not the mesh nor the model (velocity and density) then we can also
    # read the mesh and model files
    # from a single run in the beginning and broadcast them to all the others;
    # for a large number of simultaneous
    # runs for instance when solving inverse problems iteratively this can
    # DRASTICALLY reduce I/Os to disk in the solver
    # (by a factor equal to NUMBER_OF_SIMULTANEOUS_RUNS), and reducing I/Os is
    # crucial in the case of huge runs.
    # Thus, always set this option to .true. if the mesh and the model are the
    # same for all simultaneous runs.
    # In that case there is no need to duplicate the mesh and model file
    # database (the content of the DATABASES_MPI
    # directories) in each of the run0001, run0002,... directories, it is
    # sufficient to have one in run0001
    # and the code will broadcast it to the others)
    "BROADCAST_SAME_MESH_AND_MODEL":
        (False, bool, "Broadcast mesh and model for simultanous runs."),
    # -----------------------------------------------------------
    # set to true to use GPUs
    "GPU_MODE": (False, bool, "Use GPUs."),

    # ADIOS Options for I/Os
    "ADIOS_ENABLED": (False, bool, "Enable ADIOS."),
    "ADIOS_FOR_DATABASES": (False, bool, "Use ADIOS for the database."),
    "ADIOS_FOR_MESH": (False, bool, "Use ADIOS for the mesh."),
    "ADIOS_FOR_FORWARD_ARRAYS": (False, bool, "Use ADIOS for the forward "
                                              "arrays."),
    "ADIOS_FOR_KERNELS": (False, bool, "Use ADIOS for kernels.")
}


def write(config, events, stations):
    """
    Writes input files for SPECFEM3D GLOBE EPOS version.
    """
    output_files = {}

    def fbool(value):
        """
        Convert a value to a FORTRAN boolean representation.
        """
        if value:
            return ".true."
        else:
            return ".false."

    for key, value in config.iteritems():
        if isinstance(value, bool):
            config[key] = fbool(value)

    template_file = os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))),
        "specfem_globe_epos_par_file.template")
    with open(template_file, "rt") as fh:
        par_file_template = fh.read()

    par_file = par_file_template.format(**config).strip()

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
    output_files["Par_file"] = par_file
    output_files["CMTSOLUTION"] = CMT_SOLUTION_file
    output_files["STATIONS"] = "\n".join(station_parts)

    return output_files
