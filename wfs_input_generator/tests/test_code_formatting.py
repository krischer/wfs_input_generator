#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests all Python files of the project with flake8. This ensure PEP8 conformance
and some other sanity checks as well.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect
import os

import pytest


try:
    import flake8
except:  # pragma: no cover
    HAS_FLAKE8_AT_LEAST_VERSION_3 = False
else:
    if int(flake8.__version__.split(".")[0]) >= 3:
        HAS_FLAKE8_AT_LEAST_VERSION_3 = True
    else:  # pragma: no cover
        HAS_FLAKE8_AT_LEAST_VERSION_3 = False


@pytest.mark.skipif(
    not HAS_FLAKE8_AT_LEAST_VERSION_3,
    reason="Formatting test requires at least flake8 version 3.0.")
def test_flake8():
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(
        inspect.currentframe())))
    src_dir = os.path.dirname(test_dir)

    files = []
    ignore_files = []
    for dirpath, _, filenames in os.walk(src_dir):
        filenames = [_i for _i in filenames if
                     os.path.splitext(_i)[-1] == os.path.extsep + "py"]
        if not filenames:
            continue
        for py_file in filenames:
            full_path = os.path.join(dirpath, py_file)
            if full_path in ignore_files:  # pragma: no cover
                continue
            files.append(full_path)

    # Import the legacy API as flake8 3.0 currently has not official
    # public API - this has to be changed at some point.
    from flake8.api import legacy as flake8
    style_guide = flake8.get_style_guide()
    report = style_guide.check_files(files)

    # Make sure no error occured.
    assert report.total_errors == 0
