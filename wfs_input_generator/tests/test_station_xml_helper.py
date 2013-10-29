#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests the StationXML helper function.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from wfs_input_generator.station_xml_helper \
    import extract_coordinates_from_StationXML

import inspect
import io
import os

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_dictionary_extraction_from_file():
    """
    Tests the extraction of a dictionary from a StationXML file.
    """
    filename = os.path.join(DATA, "station.xml")
    coordinates = extract_coordinates_from_StationXML(filename)
    assert sorted(coordinates) == sorted([
        {"id": "HT.HORT",
         "latitude": 40.5978,
         "longitude": 23.0995,
         "elevation_in_m": 925.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.LIT",
         "latitude": 40.1003,
         "longitude": 22.489,
         "elevation_in_m": 568.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.PAIG",
         "latitude": 39.9363,
         "longitude": 23.6768,
         "elevation_in_m": 213.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.SOH",
         "latitude": 40.8206,
         "longitude": 23.3556,
         "elevation_in_m": 728.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.THE",
         "latitude": 40.6319,
         "longitude": 22.9628,
         "elevation_in_m": 124.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.XOR",
         "latitude": 39.366,
         "longitude": 23.192,
         "elevation_in_m": 500.0}
        ])


def test_dictionary_extraction_from_BytesIO():
    """
    Tests the extraction of a dictionary from a StationXML file memory file.

    For Python 2.x this should work for StringIO and BytesIO. For Python 3.x
    only BytesIO or a StationXML file without an encoding declaration.
    """
    filename = os.path.join(DATA, "station.xml")
    with open(filename, "rb") as fh:
        file_object = io.BytesIO(fh.read())
    coordinates = extract_coordinates_from_StationXML(file_object)
    assert sorted(coordinates) == sorted([
        {"id": "HT.HORT",
         "latitude": 40.5978,
         "longitude": 23.0995,
         "elevation_in_m": 925.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.LIT",
         "latitude": 40.1003,
         "longitude": 22.489,
         "elevation_in_m": 568.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.PAIG",
         "latitude": 39.9363,
         "longitude": 23.6768,
         "elevation_in_m": 213.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.SOH",
         "latitude": 40.8206,
         "longitude": 23.3556,
         "elevation_in_m": 728.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.THE",
         "latitude": 40.6319,
         "longitude": 22.9628,
         "elevation_in_m": 124.0,
         "local_depth_in_m": 0.0},
        {"id": "HT.XOR",
         "latitude": 39.366,
         "longitude": 23.192,
         "elevation_in_m": 500.0}
        ])
