#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for the waveform solver input file generator.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import inspect
import os
from setuptools import setup, find_packages


def get_package_data():
    """
    Returns a list of all files needed for the installation relativ to the
    "lasif" subfolder.
    """
    filenames = []
    # The lasif root dir.
    root_dir = os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))), "wfs_input_generator")
    # Recursively include all files in these folders:
    folders = [os.path.join(root_dir, "tests", "data")]
    for folder in folders:
        for directory, _, files in os.walk(folder):
            for filename in files:
                # Exclude hidden files.
                if filename.startswith("."):
                    continue
                filenames.append(os.path.relpath(
                    os.path.join(directory, filename),
                    root_dir))
    return filenames


setup_config = dict(
    name="wfs_input_generator",
    version="0.0.2a",
    description="Generic input file generator for waveform solvers",
    author="Lion Krischer",
    author_email="krischer@geophysik.uni-muenchen.de",
    url="http: //github.com/krischer/wfs_input_generator",
    packages=find_packages(),
    license="GNU General Public License, version 3 (GPLv3)",
    platforms="OS Independent",
    install_requires=["obspy>=1.0.1"],
    extras_require={
        "tests": ["pytest", "flake8", "mock"]},
    package_data={
        "wfs_input_generator": get_package_data()},
)

if __name__ == "__main__":
    setup(**setup_config)
