#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the SPECFEM cartesian backend.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
from wfs_input_generator import InputFileGenerator

import inspect
import numpy as np
from obspy.core import UTCDateTime
import os

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_simple():
    """
    Test a very simple SPECFEM file.
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
    gen.config.NPROC_XI = 5
    gen.config.NPROC_ETA = 5
    gen.config.RECORD_LENGTH_IN_MINUTES = 15
    gen.config.SIMULATION_TYPE = 1
    gen.config.NCHUNKS = 1
    gen.config.NEX_XI = 240
    gen.config.NEX_ETA = 240
    gen.config.NPROC_XI = 5
    gen.config.NPROC_ETA = 5
    gen.config.MODEL = "CEM_REQUEST"

    # Write the input files to a dictionary.
    input_files = gen.write(format="SPECFEM3D_GLOBE_CEM")

    assert bool(input_files)

    assert sorted(input_files.keys()) == \
        sorted(["Par_file", "CMTSOLUTION", "STATIONS"])

    # Assert the STATIONS file.
    assert input_files["STATIONS"].splitlines() == [
        "ADVT KO 41.00000 33.12340 10.0 0.0",
        "AFSR KO 40.00000 33.23450 220.0 0.0"]

    # Assert the CMTSOLUTION file.
    assert input_files["CMTSOLUTION"].splitlines() == [
        "PDE 2012 4 12 7 15 48.50 39.26000 41.04000 5.00000 4.7 4.7 "
        "2012-04-12T07:15:48.500000Z_4.7",
        "event name:      0000000",
        "time shift:       0.0000",
        "half duration:    0.0000",
        "latitude:       39.26000",
        "longitude:      41.04000",
        "depth:          5.00000",
        "Mrr:         1e+23",
        "Mtt:         1e+23",
        "Mpp:         1e+23",
        "Mrt:         0",
        "Mrp:         0",
        "Mtp:         0"]

    # Compare the Par_file to a working one.
    par_file = input_files["Par_file"]

    with open(os.path.join(DATA, "specfem_globe_cem", "Par_file")) as fh:
        expected_par_file = fh.read()

    actual_par_file_lines = par_file.splitlines()
    expected_par_file_lines = expected_par_file.splitlines()

    for actual, expected in zip(actual_par_file_lines,
                                expected_par_file_lines):
        assert actual == expected


def test_external_source_time_function():
    """
    Test a very simple SPECFEM file.
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
    gen.config.NPROC_XI = 5
    gen.config.NPROC_ETA = 5
    gen.config.RECORD_LENGTH_IN_MINUTES = 15
    gen.config.SIMULATION_TYPE = 1
    gen.config.NCHUNKS = 1
    gen.config.NEX_XI = 240
    gen.config.NEX_ETA = 240
    gen.config.NPROC_XI = 5
    gen.config.NPROC_ETA = 5
    gen.config.MODEL = "CEM_REQUEST"

    # Write the input files to a dictionary.
    input_files = gen.write(format="SPECFEM3D_GLOBE_CEM")

    # If no source time is specified the external source time function flag
    # must be false.
    assert sorted(input_files.keys()) == \
        ["CMTSOLUTION", "Par_file", "STATIONS"]
    assert "EXTERNAL_SOURCE_TIME_FUNCTION   =  .false." in \
        input_files["Par_file"]

    # Now if one is specified it should also be written.
    gen.config.SOURCE_TIME_FUNCTION = np.arange(10)

    input_files = gen.write(format="SPECFEM3D_GLOBE_CEM")

    assert sorted(input_files.keys()) == \
        ["CMTSOLUTION", "Par_file", "STATIONS", "STF"]
    assert "EXTERNAL_SOURCE_TIME_FUNCTION   =  .true." in \
        input_files["Par_file"]

    data = []
    for line in input_files["STF"].splitlines():
        if line.startswith("#"):
            continue
        data.append(float(line.strip()))
    assert data == map(float, range(10))
