#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A helper function extracting the dictionary needed for the wfs_input_generator
from a StationXML file.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from lxml import etree


def extract_coordinates_from_StationXML(file_or_file_object):
    root = etree.parse(file_or_file_object).getroot()
    namespace = root.nsmap[None]

    def _ns(tagname):
        return "{%s}%s" % (namespace, tagname)

    all_stations = []

    for network in root.findall(_ns("Network")):
        network_code = network.get("code")
        for station in network.findall(_ns("Station")):
            station_code = station.get("code")
            station_id = "%s.%s" % (network_code, station_code)
            station_latitude = _tag2obj(station, _ns("Latitude"), float)
            station_longitude = _tag2obj(station, _ns("Longitude"), float)
            station_elevation = _tag2obj(station, _ns("Elevation"), float)
            # Loop over all channels that might or might not be available. If
            # all channels have the same coordinates, use those. Otherwise use
            # the station coordinates.
            # Potential issues: The local depth is only stored at the channel
            # level and might thus not end up in the final dictionary.
            channel_coordinates = set()
            for channel in station.findall(_ns("Channel")):
                # Use a hashable dictionary to be able to use a set.
                coords = HashableDict(
                    latitude=_tag2obj(channel, _ns("Latitude"), float),
                    longitude=_tag2obj(channel, _ns("Longitude"), float),
                    elevation_in_m=_tag2obj(channel, _ns("Elevation"), float),
                    local_depth_in_m=_tag2obj(channel, _ns("Depth"), float))
                channel_coordinates.add(coords)

            # Check if it contains exactly one valid element.
            try:
                this_channel = channel_coordinates.pop()
                if len(channel_coordinates) != 0 or \
                        this_channel["latitude"] is None or \
                        this_channel["longitude"] is None or \
                        this_channel["elevation_in_m"] is None or \
                        this_channel["local_depth_in_m"] is None:
                    raise
                valid_channel = this_channel
            except:
                valid_channel = {
                    "latitude": station_latitude,
                    "longitude": station_longitude,
                    "elevation_in_m": station_elevation}
            valid_channel["id"] = station_id
            all_stations.append(valid_channel)
    return all_stations


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.iteritems())))


def _tag2obj(element, tag, convert):
    """
    Helper function extracting and converting the text of any subelement..
    """
    try:
        return convert(element.find(tag).text)
    except:
        None
