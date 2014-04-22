#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the SES3D 4.1 writer.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
from wfs_input_generator import InputFileGenerator

import glob
import inspect
import numpy as np
from obspy.core import UTCDateTime
import os
import pytest

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_real_world_example():
    """
    Test that compares the created input files to those from a real world
    example.

    The only artificial thing is the source-time function but that is
    trivial to verify.

    This is a fairly comprehensive tests but should be used in comparision
    with other unit tests.
    """
    stations = [
        {
            "id": "KO.ADVT",
            "latitude": 41.0,
            "longitude": 33.1234,
            "elevation_in_m": 10
        }, {
            "id": "KO.AFSR",
            "latitude": 40.000,
            "longitude": 33.2345,
            "elevation_in_m": 220
        }
    ]
    event = {
        "latitude": 39.260,
        "longitude": 41.040,
        "depth_in_km": 5.0,
        "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
        "m_rr": 1.0e16,
        "m_tt": 1.0e16,
        "m_pp": 1.0e16,
        "m_rt": 0.0,
        "m_rp": 0.0,
        "m_tp": 0.0}

    gen = InputFileGenerator()
    gen.add_stations(stations)
    gen.add_events(event)

    # Configure it.
    gen.config.number_of_time_steps = 4000
    gen.config.time_increment_in_s = 0.13
    gen.config.output_folder = "../DATA/OUTPUT/1.8s/"
    gen.config.mesh_min_latitude = 34.1
    gen.config.mesh_max_latitude = 42.9
    gen.config.mesh_min_longitude = 23.1
    gen.config.mesh_max_longitude = 42.9
    gen.config.mesh_min_depth_in_km = 0.0
    gen.config.mesh_max_depth_in_km = 471.0
    gen.config.nx_global = 66
    gen.config.ny_global = 108
    gen.config.nz_global = 28
    gen.config.px = 3
    gen.config.py = 4
    gen.config.pz = 4
    gen.config.source_time_function = np.linspace(1.0, 0.0, 4000)
    gen.config.stf_header = ["Some", "random", "comment"]
    gen.config.is_dissipative = False
    gen.config.adjoint_forward_wavefield_output_folder = \
        "/tmp/some_folder/"
    gen.config.displacement_snapshot_sampling = 15000
    gen.config.Q_model_relaxation_times = [1.7308, 14.3961, 22.9973]
    gen.config.Q_model_weights_of_relaxation_mechanisms = \
        [2.5100, 2.4354, 0.0879]

    # Write the input files to a dictionary.
    input_files = gen.write(format="ses3d_4_1")

    # The rest is only for asserting the produces files.
    path = os.path.join(DATA, "ses3d_4_1_real_world_example")
    for filename in glob.glob(os.path.join(path, "*")):
        with open(filename, "rt") as open_file:
            real_file = open_file.read()
        filename = os.path.basename(filename)

        if filename not in input_files:
            msg = "File '%s' has not been generated" % filename
            raise AssertionError(msg)

        lines = real_file.splitlines()
        new_lines = input_files[filename].splitlines()

        if len(lines) != len(new_lines):
            msg = (
                "File '%s' does not have the same number of lines "
                "for the real (%i lines) and generated (%i lines) "
                "input file") % (filename, len(lines), len(new_lines))
            raise AssertionError(msg)

        for line, new_line in zip(lines, new_lines):
            if line != new_line:
                msg = "Line differs in file '%s'.\n" % filename
                msg += "Expected: \"%s\"\n" % line
                msg += "Got:      \"%s\"\n" % new_line
                raise AssertionError(msg)


def test_test_all_files_have_an_empty_last_line():
    """
    Tests that all files have an empty last line.
    """
    station = {
        "id": "KO.ADVT",
        "latitude": 41.0,
        "longitude": 33.1234,
        "elevation_in_m": 10}
    event = {
        "latitude": 39.260,
        "longitude": 41.040,
        "depth_in_km": 5.0,
        "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
        "m_rr": 1.0e16,
        "m_tt": 1.0e16,
        "m_pp": 1.0e16,
        "m_rt": 0.0,
        "m_rp": 0.0,
        "m_tp": 0.0}

    gen = InputFileGenerator()
    gen.add_stations(station)
    gen.add_events(event)

    # Configure it.
    gen.config.number_of_time_steps = 4000
    gen.config.time_increment_in_s = 0.13
    gen.config.output_folder = "../DATA/OUTPUT/1.8s/"
    gen.config.mesh_min_latitude = 34.1
    gen.config.mesh_max_latitude = 42.9
    gen.config.mesh_min_longitude = 23.1
    gen.config.mesh_max_longitude = 42.9
    gen.config.mesh_min_depth_in_km = 0.0
    gen.config.mesh_max_depth_in_km = 471.0
    gen.config.nx_global = 66
    gen.config.ny_global = 108
    gen.config.nz_global = 28
    gen.config.px = 3
    gen.config.py = 4
    gen.config.pz = 4
    gen.config.source_time_function = np.linspace(1.0, 0.0, 4000)
    gen.config.is_dissipative = False

    # Write the input files to a dictionary.
    input_files = gen.write(format="ses3d_4_1")
    for input_file in input_files.itervalues():
        assert input_file.endswith("\n\n") is True


def test_wrong_stf_header_format():
    """
    Simple test asserting that the correct exceptions get raised when
    attempting to write invalid STF headers.
    """
    station = {
        "id": "KO.ADVT",
        "latitude": 41.0,
        "longitude": 33.1234,
        "elevation_in_m": 10}
    event = {
        "latitude": 39.260,
        "longitude": 41.040,
        "depth_in_km": 5.0,
        "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
        "m_rr": 1.0e16,
        "m_tt": 1.0e16,
        "m_pp": 1.0e16,
        "m_rt": 0.0,
        "m_rp": 0.0,
        "m_tp": 0.0}

    gen = InputFileGenerator()
    gen.add_stations(station)
    gen.add_events(event)

    # Configure it.
    gen.config.number_of_time_steps = 4000
    gen.config.time_increment_in_s = 0.13
    gen.config.output_folder = "../DATA/OUTPUT/1.8s/"
    gen.config.mesh_min_latitude = 34.1
    gen.config.mesh_max_latitude = 42.9
    gen.config.mesh_min_longitude = 23.1
    gen.config.mesh_max_longitude = 42.9
    gen.config.mesh_min_depth_in_km = 0.0
    gen.config.mesh_max_depth_in_km = 471.0
    gen.config.nx_global = 66
    gen.config.ny_global = 108
    gen.config.nz_global = 28
    gen.config.px = 3
    gen.config.py = 4
    gen.config.pz = 4
    gen.config.source_time_function = np.linspace(1.0, 0.0, 4000)
    gen.config.is_dissipative = False

    gen.config.stf_header = "simple string"
    # Write the input files to a dictionary.
    with pytest.raises(ValueError):
        gen.write(format="ses3d_4_1")

    gen.config.stf_header = ["1", "2", "3", "4", "5", "6"]
    # Write the input files to a dictionary.
    with pytest.raises(ValueError):
        gen.write(format="ses3d_4_1")
