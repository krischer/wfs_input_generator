#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example of how to create an input file for SES3D version 4.0.

This also (at least right now) serves as the documentation of the specific
writer.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import numpy as np
from wfs_input_generator import InputFileGenerator


def main():
    gen = InputFileGenerator()

    # SES3D 4.0 can only simulate one event at a time.
    gen.add_events("../tests/data/event1.xml")
    gen.add_stations(["../tests/data/dataless.seed.BW_FURT",
                      "../tests/data/dataless.seed.BW_RJOB"])

    # Just perform a standard forward simulation.
    gen.config.simulation_type = "normal simulation"

    gen.config.output_folder = "../OUTPUT"

    # Time configuration.
    gen.config.number_of_time_steps = 700
    gen.config.time_increment_in_s = 0.75

    # SES3D specific configuration
    gen.config.output_directory = "../DATA/OUTPUT/1.8s"
    # SES3D specific discretization
    gen.config.nx_global = 66
    gen.config.ny_global = 108
    gen.config.nz_global = 28
    gen.config.px = 3
    gen.config.py = 4
    gen.config.pz = 4

    # Specify some source time function.
    gen.config.source_time_function = np.sin(np.linspace(0, 10, 700))

    # Configure the mesh.
    gen.config.mesh_min_latitude = -50.0
    gen.config.mesh_max_latitude = 50.0
    gen.config.mesh_min_longitude = -50.0
    gen.config.mesh_max_longitude = 50.0
    gen.config.mesh_min_depth_in_km = 0.0
    gen.config.mesh_max_depth_in_km = 200.0

    # Define the rotation. Take care this is defined as the rotation of the
    # mesh.  The data will be rotated in the opposite direction! The following
    # example will rotate the mesh 5 degrees southwards around the x-axis. For
    # a definition of the coordinate system refer to the rotations.py file. The
    # rotation is entirely optional.
    gen.config.rotation_angle_in_degree = 5.0
    gen.config.rotation_axis = [1.0, 0.0, 0.0]

    # Define Q
    gen.config.is_dissipative = True
    gen.config.Q_model_relaxation_times = [1.7308, 14.3961, 22.9973]
    gen.config.Q_model_weights_of_relaxation_mechanisms = \
        [2.5100, 2.4354, 0.0879]

    # Finally write the file to a folder. If not output directory is given, a
    # dictionary containing all the files will be returned.
    gen.write(format="ses3d_4_1", output_dir="output")
    print "Written files to 'output' folder."


if __name__ == "__main__":
    main()
