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
from obspy.core import AttribDict


class Input_File_Generator(object):
    def __init__(self):
        self.config = AttribDict()

    def addEvents(self, events):
        pass

    def addStations(self, events):
        pass

    def write(self, events):
        pass
