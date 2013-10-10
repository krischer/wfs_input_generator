#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the waveform solver input file generator.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
from wfs_input_generator import InputFileGenerator

import flake8
import flake8.main
import io
import inspect
import json
from obspy.core import UTCDateTime
import os
import pytest
import warnings

# Most generic way to get the actual data directory.
DATA = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_code_formatting():
    """
    Tests the formatting and other things with flake8.
    """
    if flake8.__version__ <= "2":
        msg = ("Module was designed to be tested with flake8 >= 2.0. "
               "Please update.")
        warnings.warn(msg)
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe())))
    root_dir = os.path.dirname(os.path.dirname(test_dir))
    # Short sanity check.
    if not os.path.exists(os.path.join(root_dir, "setup.py")):
        msg = "Could not find project root."
        raise Exception(msg)
    count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        filenames = [_i for _i in filenames if
                     os.path.splitext(_i)[-1] == os.path.extsep + "py"]
        if not filenames:
            continue
        for py_file in filenames:
            full_path = os.path.join(dirpath, py_file)
            if flake8.main.check_file(full_path):
                count += 1
    assert count == 0


def test_adding_stations_as_SEED_files():
    """
    Tests adding stations as SEED files.
    """
    seed_file_1 = os.path.join(DATA, "dataless.seed.BW_FURT")
    seed_file_2 = os.path.join(DATA, "dataless.seed.BW_RJOB")

    gen = InputFileGenerator()
    gen.add_stations([seed_file_1, seed_file_2])

    # Sort to be able to compare.
    assert sorted(gen._stations) == \
        [{"id": "BW.FURT",
          "latitude": 48.162899,
          "longitude": 11.2752,
          "elevation_in_m": 565.0,
          "local_depth_in_m": 0.0},
         {"id": "BW.RJOB",
          "latitude": 47.737167,
          "longitude": 12.795714,
          "elevation_in_m": 860.0,
          "local_depth_in_m": 0.0}]


def test_adding_stations_as_SEED_files_via_BytesIO():
    """
    Tests adding stations as SEED files.
    """
    seed_file = os.path.join(DATA, "dataless.seed.BW_FURT")

    with open(seed_file, "rb") as fh:
        seed_file_mem_file = io.BytesIO(fh.read())

    gen = InputFileGenerator()
    gen.add_stations(seed_file_mem_file)

    # Sort to be able to compare.
    assert gen._stations == \
        [{"id": "BW.FURT",
          "latitude": 48.162899,
          "longitude": 11.2752,
          "elevation_in_m": 565.0,
          "local_depth_in_m": 0.0}]


def test_adding_stations_as_SAC_files():
    """
    Tests adding stations as SAC files.
    """
    sac_file = os.path.join(DATA, "example.sac")
    gen = InputFileGenerator()
    gen.add_stations(sac_file)

    assert gen._stations[0]["id"] == "IU.ANMO"
    assert round(gen._stations[0]["latitude"] - 34.94598, 5) == 0
    assert round(gen._stations[0]["longitude"] - -106.45713, 5) == 0
    assert round(gen._stations[0]["elevation_in_m"] - 1671.0, 5) == 0
    assert round(gen._stations[0]["local_depth_in_m"] - 145.0, 5) == 0


def test_adding_sac_file_without_coordinates():
    """
    This sac file has no coordinates, thus no station should actually be added.
    """
    sac_file = os.path.join(DATA, "example_without_coordinates.sac")
    gen = InputFileGenerator()
    gen.add_stations(sac_file)
    assert gen._stations == []


def test_adding_sac_file_without_local_depth():
    """
    This file has no local depth. This should be ok.
    """
    sac_file = os.path.join(DATA, "example_without_local_depth.sac")
    gen = InputFileGenerator()
    gen.add_stations(sac_file)

    assert gen._stations[0]["id"] == "IU.ANMO"
    assert round(gen._stations[0]["latitude"] - 34.94598, 5) == 0
    assert round(gen._stations[0]["longitude"] - -106.45713, 5) == 0
    assert round(gen._stations[0]["elevation_in_m"] - 1671.0, 5) == 0
    assert "local_depth_in_m" not in gen._stations[0]


def test_adding_a_single_station_dictionary():
    """
    Tests adding a single station dictionary.
    """
    station = {
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0,
        "local_depth_in_m": 10.0}
    gen = InputFileGenerator()
    gen.add_stations(station)
    assert [station] == gen._stations


def test_adding_station_as_list_of_dictionaries():
    """
    Checks that stations can also be passed as dictionaries.
    """
    stations = [{
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0,
        "local_depth_in_m": 10.0},
        {"id": "BW.RJOB",
         "latitude": 47.737167,
         "longitude": 12.795714,
         "elevation_in_m": 860.0,
         "local_depth_in_m": 2.0}]
    gen = InputFileGenerator()
    gen.add_stations(stations)
    assert sorted(stations) == sorted(gen._stations)


def test_adding_a_single_station_as_JSON():
    """
    Asserts that a single station can be added as JSON.
    """
    station = {
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0,
        "local_depth_in_m": 10.0}
    json_station = json.dumps(station)
    gen = InputFileGenerator()
    gen.add_stations(json_station)
    assert [station] == gen._stations


def test_adding_multiple_stations_as_JSON():
    """
    Tests that stations can be added as a JSON list.
    """
    stations = [{
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0,
        "local_depth_in_m": 10.0},
        {"id": "BW.RJOB",
         "latitude": 47.737167,
         "longitude": 12.795714,
         "elevation_in_m": 860.0,
         "local_depth_in_m": 2.0}]
    json_stations = json.dumps(stations)
    gen = InputFileGenerator()
    gen.add_stations(json_stations)
    assert sorted(stations) == sorted(gen._stations)


def test_adding_stations_as_StationXML():
    """
    Tests adding stations as StationXML.
    """
    stations = [
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
         "elevation_in_m": 500.0,
         "local_depth_in_m": 0.0}]
    station_xml_file = os.path.join(DATA, "station.xml")
    gen = InputFileGenerator()
    gen.add_stations(station_xml_file)
    assert sorted(stations) == sorted(gen._stations)


def test_adding_stations_as_StationXML_BytesIO():
    """
    StationXML uploading via a memory file.
    """
    stations = [
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
         "elevation_in_m": 500.0,
         "local_depth_in_m": 0.0}]
    station_xml_file = os.path.join(DATA, "station.xml")
    with open(station_xml_file, "rb") as fh:
        station_mem_file = io.BytesIO(fh.read())
    gen = InputFileGenerator()
    gen.add_stations(station_mem_file)
    assert sorted(stations) == sorted(gen._stations)


def test_adding_single_and_multiple_station():
    """
    Reading all files at once or seperate should make not difference.
    """
    seed_file_1 = os.path.join(DATA, "dataless.seed.BW_FURT")
    seed_file_2 = os.path.join(DATA, "dataless.seed.BW_RJOB")
    station_1 = {
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0,
        "local_depth_in_m": 0.0}
    station_2 = {
        "id": "BW.RJOB",
        "latitude": 47.737167,
        "longitude": 12.795714,
        "elevation_in_m": 860.0,
        "local_depth_in_m": 0.0}

    # Try with SEED files first.
    gen1 = InputFileGenerator()
    gen2 = InputFileGenerator()
    gen1.add_stations([seed_file_1, seed_file_2])
    gen2.add_stations(seed_file_1)
    gen2.add_stations(seed_file_2)
    assert sorted(gen1._stations) == sorted(gen2._stations)

    # Now try with the dictionaries.
    gen1 = InputFileGenerator()
    gen2 = InputFileGenerator()
    gen1.add_stations([station_1, station_2])
    gen2.add_stations(station_1)
    gen2.add_stations(station_2)
    assert sorted(gen1._stations) == sorted(gen2._stations)

    # Now with JSON.
    gen1 = InputFileGenerator()
    gen2 = InputFileGenerator()
    gen1.add_stations(json.dumps([station_1, station_2]))
    gen2.add_stations(json.dumps(station_1))
    gen2.add_stations(json.dumps(station_2))
    assert sorted(gen1._stations) == sorted(gen2._stations)


def test_local_depth_will_be_set_to_zero():
    """
    Tests that the local depth will be set to zero if not given.
    """
    stations = [{
        "id": "BW.FURT",
        "latitude": 48.162899,
        "longitude": 11.2752,
        "elevation_in_m": 565.0},
        {"id": "BW.RJOB",
         "latitude": 47.737167,
         "longitude": 12.795714,
         "elevation_in_m": 860.0}]
    json_stations = json.dumps(stations)
    gen = InputFileGenerator()
    gen.add_stations(stations)
    # Now add the local depth again.
    stations[0]["local_depth_in_m"] = 0.0
    stations[1]["local_depth_in_m"] = 0.0
    assert sorted(stations) == sorted(gen._stations)

    # Repeat with the JSON variant.
    gen = InputFileGenerator()
    gen.add_stations(json_stations)
    assert sorted(stations) == sorted(gen._stations)


def test_id_lat_lon_ele_are_necessary():
    """
    Tests that some station fields need to be set.
    """
    # Station with missing id.
    station_1 = {
        "latitude": 47.737167,
        "longitude": 11.2752,
        "elevation_in_m": 565.0}
    # Station with missing latitude.
    station_2 = {
        "id": "BW.FURT",
        "longitude": 11.2752,
        "elevation_in_m": 565.0}
    # Station with missing longitude.
    station_3 = {
        "id": "BW.FURT",
        "latitude": 47.737167,
        "elevation_in_m": 565.0}
    # Station with missing elevation.
    station_4 = {
        "id": "BW.FURT",
        "latitude": 47.737167,
        "longitude": 11.2752}
    # Station with everything necessary
    station_5 = {
        "id": "BW.FURT",
        "latitude": 47.737167,
        "longitude": 11.2752,
        "elevation_in_m": 565.0}

    gen = InputFileGenerator()
    # The first 4 should raise a ValueError
    with pytest.raises(ValueError):
        gen.add_stations(station_1)
    with pytest.raises(ValueError):
        gen.add_stations(station_2)
    with pytest.raises(ValueError):
        gen.add_stations(station_3)
    with pytest.raises(ValueError):
        gen.add_stations(station_4)
    # The last one not.
    gen.add_stations(station_5)

    # Do exactly the same with JSON variants.
    gen = InputFileGenerator()
    with pytest.raises(ValueError):
        gen.add_stations(json.dumps(station_1))
    with pytest.raises(ValueError):
        gen.add_stations(json.dumps(station_2))
    with pytest.raises(ValueError):
        gen.add_stations(json.dumps(station_3))
    with pytest.raises(ValueError):
        gen.add_stations(json.dumps(station_4))
    gen.add_stations(station_5)


def test_other_fields_in_station_dict_are_eliminated():
    """
    Any additional items in a station dict should be eliminated.
    """
    # Station with everything necessary
    station = {
        "id": "BW.FURT",
        "latitude": 47.737167,
        "longitude": 11.2752,
        "some_random_key": "also_has_a_field",
        "elevation_in_m": 565.0,
        "local_depth_in_m": 324.0,
        "yes!": "no"}

    gen = InputFileGenerator()
    gen.add_stations(station)
    assert gen._stations == \
        [{"id": "BW.FURT",
          "latitude": 47.737167,
          "longitude": 11.2752,
          "elevation_in_m": 565.0,
          "local_depth_in_m": 324.0}]


def test_automatic_type_converstion_for_station_dict():
    """
    Fields should undergo automatic type conversion.
    """
    # All the coordinate values should be converted to floats.
    station = {"id": "BW.FURT",
               "latitude": 1,
               "longitude": 2,
               "elevation_in_m": "3",
               "local_depth_in_m": "4"}
    gen = InputFileGenerator()
    gen.add_stations(station)
    assert type(gen._stations[0]["latitude"]) == float
    assert type(gen._stations[0]["longitude"]) == float
    assert type(gen._stations[0]["elevation_in_m"]) == float
    assert type(gen._stations[0]["local_depth_in_m"]) == float


def test_reading_QuakeML_files():
    """
    Tests the reading of QuakeML Files.
    """
    event_file_1 = os.path.join(DATA, "event1.xml")
    event_file_2 = os.path.join(DATA, "event2.xml")

    gen = InputFileGenerator()
    gen.add_events([event_file_1, event_file_2])

    # Sort to be able to compare.
    assert sorted(gen._events) == \
        [{"latitude": 45.0,
          "longitude": 12.1,
          "depth_in_km": 13.0,
          "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
          "m_rr": -2.11e+18,
          "m_tt": -4.22e+19,
          "m_pp": 4.43e+19,
          "m_rt": -9.35e+18,
          "m_rp": -8.38e+18,
          "m_tp": -6.44e+18},
         {"latitude": 13.93,
          "longitude": -92.47,
          "depth_in_km": 28.7,
          "origin_time": UTCDateTime(2012, 11, 7, 16, 35, 55, 200000),
          "m_rr": 1.02e+20,
          "m_tt": -7.96e+19,
          "m_pp": -2.19e+19,
          "m_rt": 6.94e+19,
          "m_rp": -4.08e+19,
          "m_tp": 4.09e+19}]


def test_reading_events_from_dictionary():
    """
    Tests that events can also be passed as dictionaries.
    """
    events = [{
        "latitude": 45.0,
        "longitude": 12.1,
        "depth_in_km": 13.0,
        "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
        "m_rr": -2.11e+18,
        "m_tt": -4.22e+19,
        "m_pp": 4.43e+19,
        "m_rt": -9.35e+18,
        "m_rp": -8.38e+18,
        "m_tp": -6.44e+18
    }, {
        "latitude": 13.93,
        "longitude": -92.47,
        "depth_in_km": 28.7,
        "origin_time": UTCDateTime(2012, 11, 7, 16, 35, 55, 200000),
        "m_rr": 1.02e+20,
        "m_tt": -7.96e+19,
        "m_pp": -2.19e+19,
        "m_rt": 6.94e+19,
        "m_rp": -4.08e+19,
        "m_tp": 4.09e+19}]
    gen = InputFileGenerator()
    gen.add_events(events)
    assert sorted(gen._events) == sorted(events)
