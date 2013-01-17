#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DESCRIPTION

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from wfs_input_generator import InputFileGenerator

import inspect
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


def suite():
    return unittest.makeSuite(InputFileGeneratorTestCase, "test")


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
