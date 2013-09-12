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
from setuptools import setup, find_packages

setup_config = dict(
    name="wfs_input_generator",
    version="0.0.1a",
    description="Generic input file generator for waveform solvers",
    author="Lion Krischer",
    author_email="krischer@geophysik.uni-muenchen.de",
    url="http: //github.com/krischer/wfs_input_generator",
    packages=find_packages(),
    license="GNU General Public License, version 3 (GPLv3)",
    platforms="OS Independent",
    install_requires=["obspy >=0.8.0"],
)

if __name__ == "__main__":
    setup(**setup_config)
