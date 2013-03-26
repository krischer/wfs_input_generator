#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module file first running flake8 on all files and then running all tests.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
# -*- coding: utf-8 -*-
import flake8
import flake8.main
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


def run_flake8():
    print(">>> Running flake8 on all project files...")
    if flake8.__version__ <= "2":
        msg = ("Module was designed to be tested with flake8 >= 2.0. Please "
            "update.")
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe())))
    root_dir = os.path.dirname(os.path.dirname(test_dir))
    # Short sanity check.
    if not os.path.exists(os.path.join(root_dir, "setup.py")):
        msg = "Could not find project root."
        raise Exception(msg)
    count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        filenames = [_i for _i in filenames if os.path.splitext(_i)[-1] ==
            os.path.extsep + "py"]
        if not filenames:
            continue
        for py_file in filenames:
            full_path = os.path.join(dirpath, py_file)
            if flake8.main.check_file(full_path, ignore=("E128")):
                count += 1
    if count == 0:
        print("All files OK")

if __name__ == "__main__":
    run_flake8()
    print(">>> Running tests...")
    unittest.main(defaultTest="suite")
