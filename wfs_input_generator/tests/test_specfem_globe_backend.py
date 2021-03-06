#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the SPECFEM cartesian backend commit 9e2aad47d52f97.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
from wfs_input_generator import InputFileGenerator

import inspect
from obspy.core import UTCDateTime
import os

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_against_example_file():
    """
    Tests against a known example file.
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

    # Configure it. Emulate an example in the SPECFEM directory.
    gen.config.NPROC_XI = 2
    gen.config.NPROC_ETA = 2
    gen.config.RECORD_LENGTH_IN_MINUTES = 10.0
    gen.config.SIMULATION_TYPE = 1
    gen.config.NCHUNKS = 6
    gen.config.NEX_XI = 64
    gen.config.NEX_ETA = 64
    gen.config.MODEL = "1D_isotropic_prem"

    # Non-standard values in the example file.
    gen.config.ANGULAR_WIDTH_XI_IN_DEGREES = 20.0
    gen.config.ANGULAR_WIDTH_ETA_IN_DEGREES = 20.0
    gen.config.CENTER_LATITUDE_IN_DEGREES = 40.0
    gen.config.CENTER_LONGITUDE_IN_DEGREES = 25.0
    gen.config.WRITE_SEISMOGRAMS_BY_MASTER = False
    gen.config.NTSTEP_BETWEEN_OUTPUT_INFO = 500
    gen.config.NTSTEP_BETWEEN_FRAMES = 50
    gen.config.MOVIE_COARSE = True

    # Write the input files to a dictionary.
    input_files = gen.write(format="SPECFEM3D_GLOBE")

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

    par_file = input_files["Par_file"]
    assert "SIMULATION_TYPE" in par_file
    assert "NSTEP" in par_file

    # Example Par_file from the repository.
    original_par_file = os.path.join(DATA, "specfem_globe",
                                     "Par_file")
    with open(original_par_file, "rt") as fh:
        original_par_file = fh.read().strip()
    assert original_par_file == par_file


def test_cmt_file():
    """
    Test the cmt file.
    """
    stations = [
        {
            "id": "KO.ADVT",
            "latitude": 41.0,
            "longitude": 33.1234,
            "elevation_in_m": 10
        }
    ]

    gen = InputFileGenerator()
    gen.add_stations(stations)

    event_file = os.path.join(DATA, "quakeml_multiple_origins.xml")
    gen.add_events(event_file)

    # Configure it. Emulate an example in the SPECFEM directory.
    gen.config.NPROC_XI = 2
    gen.config.NPROC_ETA = 2
    gen.config.RECORD_LENGTH_IN_MINUTES = 10.0
    gen.config.SIMULATION_TYPE = 1
    gen.config.NCHUNKS = 6
    gen.config.NEX_XI = 64
    gen.config.NEX_ETA = 64
    gen.config.MODEL = "1D_isotropic_prem"

    # Write the input files to a dictionary.
    input_files = gen.write(format="SPECFEM3D_GLOBE")

    assert bool(input_files)

    assert sorted(input_files.keys()) == \
        sorted(["Par_file", "CMTSOLUTION", "STATIONS"])

    # Assert the CMTSOLUTION file.
    assert input_files["CMTSOLUTION"].splitlines() == [
        "PDE 2013 6 9 14 22 15.60 -26.00000 132.09000 12.00000 5.3 5.3 "
        "2013-06-09T14:22:15.600000Z_5.3",
        "event name:      0000000",
        "time shift:       0.0000",
        "half duration:    0.0000",
        "latitude:       -26.00000",
        "longitude:      132.09000",
        "depth:         12.00000",
        "Mrr:         1.05e+24",
        "Mtt:         -8.23e+23",
        "Mpp:         -2.29e+23",
        "Mrt:         2e+22",
        "Mrp:         2.8e+23",
        "Mtp:         1.65e+24"]
