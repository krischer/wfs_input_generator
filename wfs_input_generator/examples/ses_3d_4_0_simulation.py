#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example of how to create an input file for SES3D version 4.0.

This also (at least right now) serves as the documentation of the specific
writer.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from wfs_input_generator import InputFileGenerator

gen = InputFileGenerator()

# SES3D 4.0 can only simulate one event at a time.
gen.add_events("../tests/data/event1.xml")
gen.add_stations(["../tests/data/dataless.seed.BW_FURT",
    "../tests/data/dataless.seed.BW_RJOB"])

# Time configuration. Should be self-explanatory.
gen.config.time_config.time_steps = 700
gen.config.time_config.time_delta = 0.75

# SES3D specific configuration
gen.config.output_directory = "../DATA/OUTPUT/1.8s"
gen.config.forward_wavefield_output_folder = "tmp/DATABASES_MPI/fichtner/"
gen.config.simulation_type = "normal simulation"

# Discretization
gen.config.nx_global = 66
gen.config.ny_global = 108
gen.config.nz_global = 28
gen.config.px = 3
gen.config.py = 4
gen.config.pz = 4

# Configure the mesh.
gen.config.mesh.min_latitude = -10.0
gen.config.mesh.max_latitude = 10.0
gen.config.mesh.min_longitude = 0.0
gen.config.mesh.max_longitude = 20.0
gen.config.mesh.min_depth = 0.0
gen.config.mesh.max_depth = 200.0

# Define the rotation. Take care this is defined as the rotation of the mesh.
# The data will be rotated in the opposite direction! The following example
# will rotate the mesh 5 degrees southwards around the x-axis. For a definition
# of the coordinate system refer to the rotations.py file. The rotation is
# entirely optional.
gen.config.mesh.rotation_angle = [1.0, 0.0, 0.0]
gen.config.mesh.rotation_axis = 5.0

gen.write(format="ses3d_4_0", output_dir="output")
