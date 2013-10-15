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

import glob
import inspect
import numpy as np
from obspy.core import UTCDateTime
import os

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_simple():
    """
    Very Barebones test. Just assert that some files are actually created.
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
