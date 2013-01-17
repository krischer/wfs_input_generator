#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file write for SES3D SVN revision 276.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import os


def write(config, events, stations, output_directory):
    """
    """
    parts = []
    for station in stations:
        parts.append(_station_to_receiver_string(station))

    output_file = os.path.join(output_directory, "input_file.txt")

    with open(output_file, "wb") as open_file:
        open_file.write("\n".join(parts))


def _station_to_receiver_string(station):
    rec_string = (
    "&receiver\n"
    "    network = '{network}'\n"
    "    station = '{station}'\n"
    "    lat = {latitude}\n"
    "    lon = {longitude}\n"
    "    depth = {depth_in_km}\n"
    "    attributes = 'vx', 'vy', 'vz'\n"
    "/\n")
    rec_string = rec_string.format(
        network=station["id"].split(".")[0],
        station=station["id"].split(".")[1],
        latitude=station["latitude"],
        longitude=station["longitude"],
        # XXX: Can depth be negative? Set to zero for now...
        depth_in_km=0.0)
    return rec_string
