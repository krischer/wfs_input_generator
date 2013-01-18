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

# Configure the mesh. Make it have ten elements in each direction.
gen.config.mesh = SphericalSectionMesh()
gen.config.mesh.n_north_south = 10
gen.config.mesh.n_west_east = 10
gen.config.mesh.n_down_up = 10
gen.config.mesh.min_latitude = -10.0
gen.config.mesh.max_latitude = 10.0
gen.config.mesh.min_longitude = 0.0
gen.config.mesh.max_latitude = 20.0
gen.config.mesh.min_depth = 0.0
gen.config.mesh.max_depth = 200.0
# Put any solver specific mesh specification here.
gen.config.mesh.config.lagrange_polynomial_degree = 4
gen.config.mesh.config.width_of_relaxing_boundaries = 2

gen.write(format="ses3d_svnr276", output_dir="output")
