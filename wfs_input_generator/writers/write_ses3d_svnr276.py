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

    for event in events:
        parts.append(_event_to_source_string(event))


    output_file = os.path.join(output_directory, "input_file.txt")

    with open(output_file, "wb") as open_file:
        open_file.write("\n".join(parts))


def _event_to_source_string(event):
    # For the moment tensor: r is up, t is south and p is east
    # In SES3D: x is south, y is east, z is down
    src_string = (
    "&source\n"
    "    lat = {latitude}\n"
    "    lon = {longitude}\n"
    "    depth = {depth_in_km}\n"
    "    wavelet = 'RICKER'\n"
    "    moment_tensor = {m_tt}, {m_tp}, {m_tr}, {m_pp}, {m_pr}, {m_rr}\n"
    "/\n")
    src_string = src_string.format(
        latitude=event["latitude"],
        longitude=event["longitude"],
        depth_in_km=event["depth_in_km"],
        m_tt=event["m_tt"],
        m_tp=event["m_tp"],
        m_tr=event["m_rt"],
        m_pp=event["m_pp"],
        m_pr=event["m_rp"],
        m_rr=event["m_rr"])
    return src_string


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
