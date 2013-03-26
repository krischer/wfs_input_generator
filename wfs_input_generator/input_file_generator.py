#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An attempt to create a generic input file generator for different waveform
solvers.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import glob
import inspect
from obspy import readEvents
from obspy.core import AttribDict, read
from obspy.core.event import Event
from obspy.sac.core import isSAC
from obspy.xseed import Parser
import os


def unique_list(items):
    """
    Helper function taking a list of items and returning a list with duplicate
    items removed.
    """
    output = []
    for item in items:
        if item not in output:
            output.append(item)
    return output


class InputFileGenerator(object):
    """
    """
    def __init__(self):
        self.config = AttribDict()
        self.config.time_config = AttribDict()
        self.config.mesh = AttribDict()
        self.config.model = None
        self._events = []
        self._stations = []

    def add_events(self, events):
        """
        Add one or more events to the input file generator. Most inversions
        should specify only one event but some codes can deal with multiple
        events.

        Can currently deal with QuakeML files and obspy.core.event.Event
        objects.

        :type events: list or obspy.core.event.Catalog object
        :param events: A list of filenames, a list of obspy.core.event.Event
            objects, or an obspy.core.event.Catalog object.
        """
        if isinstance(events, Event) or isinstance(events, dict) or \
                not hasattr(events, "__iter__"):
            events = [events, ]

        for event in events:
            if isinstance(event, Event):
                self._parse_event(event)
                continue
            elif isinstance(event, dict):
                self._events.append(event)
                continue
            try:
                cat = readEvents(event)
            except:
                msg = "Could not read %s." % str(event)
                raise TypeError(msg)
            for event in cat:
                self._parse_event(event)
        # Make sure each event is unique.
        self._events = unique_list(self._events)

    def add_stations(self, stations):
        """
        Add the desired output stations to the input file generator.

        Can currently deal with SEED/XML-SEED files and dictionaries of the
        following form:

            {"latitude": 123.4,
             "longitude": 123.4,
             "elevation_in_m": 123.4,
             "local_depth_in_m": 123.4,
             "id": "network_code.station_code"}

        `local_depth_in_m` is optional and will be assumed to be zero if not
        present. It denotes the burrial of the sensor beneath the surface.

        If it is a SEED/XML-SEED files, all stations in it will be added.

        :type stations: List of filenames, list of dictionaries or a single
            filename, single dictionary.
        :param stations: The stations for which output files should be
            generated.
        """
        all_stations = {}
        # Thin wrapper to enable single element treatment.
        if isinstance(stations, dict) or not hasattr(stations, "__iter__"):
            stations = [stations, ]
        for station_item in stations:
            if isinstance(station_item, dict):
                if "latitude" not in station_item or \
                        "longitude" not in station_item or \
                        "elevation_in_m" not in station_item or \
                        "id" not in station_item:
                    msg = ("Each station dictionary needs to at least have "
                        "'latitude', 'longitude', 'elevation_in_m', and 'id' "
                        "keys.")
                    raise ValueError(msg)
                # Create new dict to not carry around any additional keys.
                stat = {
                    "latitude": float(station_item["latitude"]),
                    "longitude": float(station_item["longitude"]),
                    "elevation_in_m": float(station_item["elevation_in_m"]),
                    "id": str(station_item["id"])}
                if "local_depth_in_m" in station_item:
                    stat["local_depth_in_m"] = \
                        float(station_item["local_depth_in_m"])
                else:
                    stat["local_depth_in_m"] = 0.0
                if stat["id"] in all_stations:
                    all_stations[stat["id"]].update(stat)
                else:
                    all_stations[stat["id"]] = stat
                continue
            # Check if the file is a sac file.
            if isSAC(station_item):
                st = read(station_item)
                for tr in st:
                    stat = {}
                    stat["id"] = "%s.%s" % (tr.stats.network,
                        tr.stats.station)
                    stat["latitude"] = float(tr.stats.sac.stla)
                    stat["longitude"] = float(tr.stats.sac.stlo)
                    stat["elevation_in_m"] = float(tr.stats.sac.stel)
                    stat["local_depth_in_m"] = float(tr.stats.sac.stdp)
                    if stat["id"] in all_stations:
                        all_stations[stat["id"]].update(stat)
                    else:
                        all_stations[stat["id"]] = stat
                    continue
                continue

            # Check if the file is readable by the parser.
            try:
                Parser(station_item)
                is_seed = True
            except:
                is_seed = False
            if is_seed is True:
                self._parse_seed(station_item, all_stations)
                continue

            msg = "Warning: Could not read %s." % station_item
            print msg

        self._stations.extend(list(all_stations.values()))
        self._stations = unique_list(self._stations)

    def _parse_seed(self, station_item, all_stations):
        """
        Helper function to parse SEED and XSEED files.
        """
        parser = Parser(station_item)
        for station in parser.stations:
            network_code = None
            station_code = None
            latitude = None
            longitude = None
            elevation = None
            local_depth = None
            for blockette in station:
                if blockette.id not in [50, 52]:
                    continue
                elif blockette.id == 50:
                    network_code = str(blockette.network_code)
                    station_code = str(blockette.station_call_letters)
                    continue
                elif blockette.id == 52:
                    latitude = blockette.latitude
                    longitude = blockette.longitude
                    elevation = blockette.elevation
                    local_depth = blockette.local_depth
                    break
            if None in [network_code, station_code, latitude, longitude,
                    elevation, local_depth]:
                msg = "Could not parse %s" % station_item
                raise ValueError(msg)
            stat = {
                "id": "%s.%s" % (network_code, station_code),
                "latitude": latitude,
                "longitude": longitude,
                "elevation_in_m": elevation,
                "local_depth_in_m": local_depth}
            if stat["id"] in all_stations:
                all_stations[stat["id"]].update(stat)
            else:
                all_stations[stat["id"]] = stat

    def write(self, format, output_dir):
        """
        Write an input file with the specified format.

        :type format: string
        :param format: The requested format of the generated input files. Get a
            list of available format with a call to
            self.get_available_formats().
        :type output_dir: string
        :param output_dir: The folder where all files will be written to. If
            it does not exists, it will be created. Any files already in
            existence WILL be overwritten. So be careful.
        """
        # Check if the corresponding write function exists.
        self.__find_write_scripts()
        if format not in list(self.__write_functions.keys()):
            msg = "Format %s not found. Available formats: %s." % (format,
                list(self.__write_functions.keys()))
            raise ValueError(msg)
        # Create the folder if it does not exist.
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.isdir(output_dir):
            msg = "output_dir %s is not a directory" % output_dir
            raise ValueError(msg)
        output_dir = os.path.abspath(output_dir)
        # Make sure only unique stations and events are passed on.
        self._stations = unique_list(self._stations)
        self._events = unique_list(self._events)
        # Call the write function. The write function is supposed to raise the
        # appropriate error in case anything is amiss.
        self.__write_functions[format](config=self.config,
            events=self._events, stations=self._stations,
            output_directory=output_dir)

    def __find_write_scripts(self):
        """
        Helper method to find all available writer script. A write script is
        defined as being in the folder "writer" and having a name of the form
        "write_XXX.py". It furthermore needs to have a write() method.
        """
        # Most generic way to get the 'writers' subdirectory.
        write_dir = os.path.join(os.path.dirname(inspect.getfile(
            inspect.currentframe())), "writers")
        files = glob.glob(os.path.join(write_dir, "write_*.py"))
        import_names = [os.path.splitext(os.path.basename(_i))[0] for _i in
            files]
        write_functions = {}
        for name in import_names:
            module_name = "writers.%s" % name
            try:
                module = __import__(module_name, globals(), locals(),
                    ["write"], -1)
                function = module.write
            except Exception as e:
                print("Warning: Could not import %s." % (module_name))
                print("\t%s: %s" % (e.__class__.__name__, str(e)))
            if not hasattr(function, "__call__"):
                msg = "Warning: write in %s is not a function." % module_name
                print(msg)
                continue
            write_functions[name[6:]] = function
        self.__write_functions = write_functions

    def get_available_formats(self):
        """
        Get a list of all available formats.
        """
        self.__find_write_scripts()
        return list(self.__write_functions.keys())

    def _parse_event(self, event):
        """
        Check and parse events.

        Each event at least needs to have an origin and a moment tensor,
        otherwise an error will be raised.
        """
        # Do a lot of checks first to be able to give descriptive error
        # messages.
        if not event.origins:
            msg = "Each event needs to have an origin."
            raise ValueError(msg)
        if not event.focal_mechanisms:
            msg = "Each event needs to have a focal mechanism."
            raise ValueError(msg)
        # Choose either the preferred origin or the first one.
        origin = event.preferred_origin() or event.origins[0]
        # Same with the focal mechanism.
        foc_mec = event.preferred_focal_mechanism() or \
            event.focal_mechanisms[0]
        # Origin needs to have latitude, longitude, depth and time
        if not origin.latitude or not origin.longitude or not origin.depth \
                or not origin.time:
            msg = ("Every event origin needs to have latitude, longitude, "
                "depth and time")
            raise ValueError(msg)
        # The focal mechanism of course needs to have a moment tensor.
        if not foc_mec.moment_tensor or not foc_mec.moment_tensor.tensor:
            msg = "Every event needs to have a moment tensor."
            raise ValueError(msg)
        # Also all six components need to be specified.
        mt = foc_mec.moment_tensor.tensor
        if not mt.m_rr or not mt.m_tt or not mt.m_pp or not mt.m_rt \
                or not mt.m_rp or not mt.m_tp:
            msg = "Every event needs all six moment tensor components."
            raise ValueError(msg)

        # Now the event should be valid.
        self._events.append({
            "latitude": origin.latitude,
            "longitude": origin.longitude,
            "depth_in_km": origin.depth / 1000.0,
            "origin_time": origin.time,
            "m_rr": mt.m_rr,
            "m_tt": mt.m_tt,
            "m_pp": mt.m_pp,
            "m_rt": mt.m_rt,
            "m_rp": mt.m_rp,
            "m_tp": mt.m_tp})
