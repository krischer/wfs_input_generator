#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example of how to create an input file for a certain SES3D version.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from wfs_input_generator import InputFileGenerator
from wfs_input_generator.mesh import SphericalSectionMesh

import os

gen = InputFileGenerator()

# Paths to the used event and station data.
data_path = os.path.join(os.pardir, "tests", "data")
gen.add_events(os.path.join(data_path, "event1.xml"))
gen.add_stations([os.path.join(data_path, "dataless.seed.BW_FURT"),
    os.path.join(data_path, "dataless.seed.BW_RJOB")])

# Time configuration
gen.config.time_config.time_steps = 700
gen.config.time_config.time_delta = 0.75

# SES3D specific configuration
gen.config.output_directory = "../DATA/OUTPUT/1.8s"
gen.config.forward_wavefield_output_folder = "tmp/DATABASES_MPI/fichtner/"
gen.config.simulation_type = "normal simulation"

gen.config.nx_global = 66
gen.config.ny_global = 108
gen.config.nz_global = 28
gen.config.px = 3
gen.config.py = 4
gen.config.pz = 4

# Configure the mesh. Make it have ten elements in each direction.
gen.config.mesh.min_latitude = -10.0
gen.config.mesh.max_latitude = 10.0
gen.config.mesh.min_longitude = 0.0
gen.config.mesh.max_longitude = 20.0
gen.config.mesh.min_depth = 0.0
gen.config.mesh.max_depth = 200.0

gen.write(format="ses3d_4_0", output_dir="output")
