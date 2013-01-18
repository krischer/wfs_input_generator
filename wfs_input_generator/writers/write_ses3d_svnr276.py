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

    parts.append(_time_config(config.time_config))

    parts.append(_write_grid_block(config))

    parts.append(_write_model_block(config))

    for station in stations:
        parts.append(_station_to_receiver_string(station))

    for event in events:
        parts.append(_event_to_source_string(event))

    output_file = os.path.join(output_directory, "input_file.txt")

    with open(output_file, "wb") as open_file:
        open_file.write("\n".join(parts))


def _write_grid_block(config):
    """
    Helper function to write the grid block.
    """
    template = (
        "&grid\n"
        "    nx = {nx}\n"
        "    ny = {ny}\n"
        "    nz = {nz}\n"
        "    lpd = {lpd}\n"
        "    pml = {pml}\n"
        "/\n")
    return template.format(
        nx=config.mesh.n_north_south,
        ny=config.mesh.n_west_east,
        nz=config.mesh.n_down_up,
        lpd=config.mesh.config.lagrange_polynomial_degree,
        pml=config.mesh.config.width_of_relaxing_boundaries)

def _write_model_block(config):
    """
    Helper function to write the model block.
    """
    template = (
        "&model\n"
        "    lat_min = {lat_min}\n"
        "    lat_max = {lat_max}\n"
        "    lon_min = {lon_min}\n"
        "    lon_max = {lon_max}\n"
        "    rad_min = {rad_min}\n"
        "    rad_max = {rad_max}\n"
        "    model_name = 'PREM'\n"
        "    rhoinv = './rhoinv'\n"
        "    mu = './mu'\n"
        "    a = './a'\n"
        "    b = './b'\n"
        "    c = './c'\n"
        "    q = './q'\n"
        "/\n")
    return template.format(
        lat_min=config.mesh.min_latitude,
        lat_max=config.mesh.max_latitude,
        lon_min=config.mesh.min_longitude,
        lon_max=config.mesh.max_longitude,
        rad_min=config.mesh.min_depth,
        rad_max=config.mesh.max_depth)

def _time_config(time_config):
    template = (
        "&time\n"
        "    nt = {time_steps}\n"
        "    dt = {time_delta}\n"
        "/\n")
    return template.format(
        time_steps=time_config.time_steps,
        time_delta=time_config.time_delta)


def _event_to_source_string(event):
    # For the moment tensor: r is up, t is south and p is east
    # In SES3D: x is south, y is east, z is down
    src_string = (
        "&source\n"
        "    lat = {latitude}\n"
        "    lon = {longitude}\n"
        "    depth = {depth_in_km}\n"
        "    wavelet = 'RICKER'\n"
        "    moment_tensor = {m_tt} {m_tp} {m_tr} {m_pp} {m_pr} {m_rr}\n"
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
