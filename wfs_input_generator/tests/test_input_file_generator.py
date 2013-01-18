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

import inspect
from obspy.core import UTCDateTime
import os
import unittest


class InputFileGeneratorTestCase(unittest.TestCase):
    """
    Test case for the general InputFileGenerator.
    """
    def setUp(self):
        # Most generic way to get the actual data directory.
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()))), "data")

    def test_readingSEEDFiles(self):
        """
        Tests the reading of SEED files.
        """
        seed_file_1 = os.path.join(self.data_dir, "dataless.seed.BW_FURT")
        seed_file_2 = os.path.join(self.data_dir, "dataless.seed.BW_RJOB")

        gen = InputFileGenerator()
        gen.add_stations([seed_file_1, seed_file_2])

        # Sort to be able to compare.
        stations = sorted(gen._stations)
        self.assertEqual([
            {"id": "BW.FURT",
             "latitude": 48.162899,
             "longitude": 11.2752,
             "elevation_in_m": 565.0,
             "local_depth_in_m": 0.0},
            {"id": "BW.RJOB",
             "latitude": 47.737167,
             "longitude": 12.795714,
             "elevation_in_m": 860.0,
             "local_depth_in_m": 0.0}], stations)

    def test_readingQuakeMLFiles(self):
        """
        Tests the reading of QuakeML Files.
        """
        event_file_1 = os.path.join(self.data_dir, "event1.xml")
        event_file_2 = os.path.join(self.data_dir, "event2.xml")

        gen = InputFileGenerator()
        gen.add_events([event_file_1, event_file_2])

        # Sort to be able to compare.
        events = sorted(gen._events)
        self.assertEqual([{
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
            "m_tp": 4.09e+19
            }], events)


def suite():
    return unittest.makeSuite(InputFileGeneratorTestCase, "test")


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
