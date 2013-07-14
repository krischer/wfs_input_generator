#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Autodiscovery of all tests for the module.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import glob
import inspect
import os
import unittest
import warnings


def suite():
    """
    Automatic unittest discovery.

    Will discover all test suites in files called test*.py in the tests folder.
    """
    # Get a list of all files.
    files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))), "test*.py"))
    files = [os.path.splitext(os.path.basename(_i))[0] for _i in files]

    modules = []
    # try to import all files.
    for module in files:
        try:
            module = __import__(module, globals(), locals())
        except:
            warnings.warn("Module %s could not be imported" % module)
            continue
        modules.append(module)

    suite = unittest.TestSuite()
    for module in modules:
        for attrib in dir(module):
            value = getattr(module, attrib)
            try:
                if issubclass(value, unittest.TestCase):
                    suite.addTest(unittest.makeSuite(value, "test"))
            except:
                pass
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
