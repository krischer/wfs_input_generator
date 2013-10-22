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
    gen.config.NPROC = 5
    gen.config.NSTEP = 10
    gen.config.DT = 15
    gen.config.SIMULATION_TYPE = 1

    # Write the input files to a dictionary.
    input_files = gen.write(format="SPECFEM3D_CARTESIAN")

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

    # XXX: Extend test.
    par_file = input_files["Par_file"]
    assert "SIMULATION_TYPE" in par_file
    assert "NSTEP" in par_file
