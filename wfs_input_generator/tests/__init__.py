# -*- coding: utf-8 -*-
import flake8.main
import inspect
import os
import unittest

# Import the necessary files and append them to a list. These modules will be
# searched for unittests.
import test_input_file_generator
modules = (test_input_file_generator, )


def suite():
    """
    Automatic unittest discovery.
    """
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
