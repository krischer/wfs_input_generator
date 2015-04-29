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
from wfs_input_generator.station_xml_helper \
    import extract_coordinates_from_StationXML

import copy
import fnmatch
import glob
import inspect
import io
import json
import obspy
from obspy import readEvents
from obspy.core import AttribDict, read
from obspy.core.event import Event
from obspy.xseed import Parser
import os
import pkg_resources
import urllib2
import warnings

# Proper way to get the is_sac function.
is_sac = pkg_resources.load_entry_point(
    "obspy", "obspy.plugin.waveform.SAC", "isFormat")


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
        self._events = []
        self._stations = []
        self.__station_filter = None
        self.__event_filter = None

    def add_configuration(self, config):
        """
        Adds all items in config to the configuration.

        Useful for bulk configuration from external sources.

        :type config: dict or str
        :param config: Contains the new configuration items. Can be either a
            dictionary or a JSON document.
        """
        try:
            doc = json.loads(config)
        except:
            pass
        else:
            if isinstance(doc, dict):
                config = doc

        if not isinstance(config, dict):
            msg = "config must be either a dict or a single JSON document"
            raise ValueError(msg)

        self.config.__dict__.update(config)

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
        # Try to interpret it as json. If it works and results in a list or
        # dicionary, use it!
        try:
            json_e = json.loads(events)
        except:
            pass
        else:
            # A simple string is also a valid JSON document.
            if isinstance(json_e, list) or isinstance(json_e, dict):
                events = json_e

        # Thin wrapper to enable single element treatment.
        if isinstance(events, Event) or isinstance(events, dict) or \
                not hasattr(events, "__iter__") or \
                (hasattr(events, "read") and
                 hasattr(events.read, "__call__")):
            events = [events, ]

        # Loop over all events.
        for event in events:
            # Download it if it is some kind of URL.
            if isinstance(event, basestring) and "://" in event:
                event = io.BytesIO(urllib2.urlopen(event).read())

            if isinstance(event, Event):
                self._parse_event(event)
                continue
            # If it is a dict do some checks and add it.
            elif isinstance(event, dict):
                required_keys = ["latitude", "longitude", "depth_in_km",
                                 "origin_time", "m_rr", "m_tt", "m_pp", "m_rt",
                                 "m_rp", "m_tp"]
                for key in required_keys:
                    if key not in event:
                        msg = (
                            "Each station events needs to at least have "
                            "{keys} keys.").format(
                            keys=", ".join(required_keys))
                        raise ValueError(msg)
                # Create new dict to not carry around any additional keys.
                ev = {
                    "latitude": float(event["latitude"]),
                    "longitude": float(event["longitude"]),
                    "depth_in_km": float(event["depth_in_km"]),
                    "origin_time": obspy.UTCDateTime(event["origin_time"]),
                    "m_rr": float(event["m_rr"]),
                    "m_tt": float(event["m_tt"]),
                    "m_pp": float(event["m_pp"]),
                    "m_rt": float(event["m_rt"]),
                    "m_rp": float(event["m_rp"]),
                    "m_tp": float(event["m_tp"])}
                if "description" in event and \
                        event["description"] is not None:
                    ev["description"] = str(event["description"])
                else:
                    ev["description"] = None
                self._events.append(ev)
                continue

            try:
                cat = readEvents(event)
            except:
                pass
            else:
                for event in cat:
                    self._parse_event(event)
                continue

            msg = "Could not read %s." % event
            raise ValueError(msg)
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
        # Try to interpret it as json. If it works and results in a list or
        # dicionary, use it!
        try:
            json_s = json.loads(stations)
        except:
            pass
        else:
            # A simple string is also a valid JSON document.
            if isinstance(json_s, list) or isinstance(json_s, dict):
                stations = json_s

        # Thin wrapper to enable single element treatment.
        if isinstance(stations, dict) or not hasattr(stations, "__iter__") or \
                (hasattr(stations, "read") and
                 hasattr(stations.read, "__call__")):
            stations = [stations, ]

        all_stations = {}

        for station_item in stations:
            # Store the original pointer position to be able to restore it.
            original_position = None
            try:
                original_position = station_item.tell()
                station_item.seek(original_position, 0)
            except:
                pass

            # Download it if it is some kind of URL.
            if isinstance(station_item, basestring) and "://" in station_item:
                station_item = io.BytesIO(urllib2.urlopen(station_item).read())

            # If it is a dict do some checks and add it.
            if isinstance(station_item, dict):
                if "latitude" not in station_item or \
                        "longitude" not in station_item or \
                        "elevation_in_m" not in station_item or \
                        "id" not in station_item:
                    msg = (
                        "Each station dictionary needs to at least have "
                        "'latitude', 'longitude', 'elevation_in_m', and 'id' "
                        "keys.")
                    raise ValueError(msg)
                # Create new dict to not carry around any additional keys.
                stat = {
                    "latitude": float(station_item["latitude"]),
                    "longitude": float(station_item["longitude"]),
                    "elevation_in_m": float(station_item["elevation_in_m"]),
                    "id": str(station_item["id"])}
                try:
                    stat["local_depth_in_m"] = \
                        float(station_item["local_depth_in_m"])
                except:
                    pass
                all_stations[stat["id"]] = stat
                continue

            # Also accepts SAC files.
            if is_sac(station_item):
                st = read(station_item)
                for tr in st:
                    stat = {}
                    stat["id"] = "%s.%s" % (tr.stats.network,
                                            tr.stats.station)
                    stat["latitude"] = float(tr.stats.sac.stla)
                    stat["longitude"] = float(tr.stats.sac.stlo)
                    stat["elevation_in_m"] = float(tr.stats.sac.stel)
                    stat["local_depth_in_m"] = float(tr.stats.sac.stdp)
                    # lat/lng/ele must be given.
                    if stat["latitude"] == -12345.0 or \
                            stat["longitude"] == -12345.0 or \
                            stat["elevation_in_m"] == -12345.0:
                        warnings.warn("No coordinates for channel '%s'."
                                      % str(tr))
                        continue
                    # Local may be neclected.
                    if stat["local_depth_in_m"] == -12345.0:
                        del stat["local_depth_in_m"]
                    all_stations[stat["id"]] = stat
                    continue
                continue

            # Reset pointer.
            if original_position is not None:
                station_item.seek(original_position, 0)

            # SEED / XML-SEED
            try:
                Parser(station_item)
                is_seed = True
            except:
                is_seed = False
            # Reset.
            if original_position is not None:
                station_item.seek(original_position, 0)
            if is_seed is True:
                self._parse_seed(station_item, all_stations)
                continue

            # StationXML
            try:
                stations = extract_coordinates_from_StationXML(station_item)
            except:
                pass
            else:
                for station in stations:
                    all_stations[station["id"]] = station
                continue

            msg = "Could not read %s." % station_item
            raise ValueError(msg)

        self.__add_stations(all_stations.values())

    def __add_stations(self, stations):
        """
        Helper function to assure all supported file formats result in the same
        station dictionary format.

        Will set the local depth to zero if not found. Should work across all
        formats.
        """
        _s = []
        for station_item in stations:
            station = {"latitude": float(station_item["latitude"]),
                       "longitude": float(station_item["longitude"]),
                       "elevation_in_m": float(station_item["elevation_in_m"]),
                       "id": str(station_item["id"])}
            try:
                station["local_depth_in_m"] = \
                    float(station_item["local_depth_in_m"])
            except:
                station["local_depth_in_m"] = 0.0
            _s.append(station)
        self._stations.extend(_s)
        self._stations = unique_list(self._stations)

    @property
    def _filtered_stations(self):
        if not self.station_filter:
            return self._stations

        def filt(station):
            for pattern in self.station_filter:
                if fnmatch.fnmatch(station["id"], pattern):
                    return True
            return False

        return filter(filt, self._stations)

    @property
    def station_filter(self):
        return self.__station_filter

    @station_filter.setter
    def station_filter(self, value):
        try:
            value = json.loads(value)
        except:
            pass

        if not hasattr(value, "__iter__") and value is not None:
            msg = "Needs to be a list or other iterable."
            raise TypeError(msg)
        self.__station_filter = value

    @property
    def _filtered_events(self):
        if not self.event_filter:
            return self._events

        def filt(event):
            # No id will remove the event.
            if "_event_id" not in event:
                return False

            for event_id in self.event_filter:
                if event["_event_id"].lower() == event_id.lower():
                    return True
            return False

        return filter(filt, self._events)

    @property
    def event_filter(self):
        return self.__event_filter

    @event_filter.setter
    def event_filter(self, value):
        try:
            value = json.loads(value)
        except:
            pass

        if not hasattr(value, "__iter__") and value is not None:
            msg = "Needs to be a list or other iterable."
            raise TypeError(msg)
        self.__event_filter = value

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

    def write(self, format, output_dir=None):
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
            msg = "Format %s not found. Available formats: %s." % (
                format, list(self.__write_functions.keys()))
            raise ValueError(msg)

        # Make sure only unique stations and events are passed on. Sort
        # stations by id.
        _stations = copy.deepcopy(sorted(unique_list(self._filtered_stations),
                                         key=lambda x: x["id"]))
        _events = copy.deepcopy(unique_list(self._filtered_events))
        # Remove the "_event_id"s everywhere
        for event in _events:
            try:
                del event["_event_id"]
            except:
                pass

        # Set the correct write function.
        writer = self.__write_functions[format]
        config = copy.deepcopy(self.config)

        # Check that all required configuration values exist and convert to
        # the correct type.
        for config_name, value in writer["required_config"].iteritems():
            convert_fct, _ = value
            if config_name not in config:
                msg = ("The input file generator for '%s' requires the "
                       "configuration item '%s'.") % (format, config_name)
                raise ValueError(msg)
            try:
                config[config_name] = convert_fct(config[config_name])
            except:
                msg = ("The configuration value '%s' could not be converted "
                       "to '%s'") % (config_name, str(convert_fct))
                raise ValueError(msg)

        # Now set the optional and default parameters.
        for config_name, value in writer["default_config"].iteritems():
            default_value, convert_fct, _ = value
            if config_name in config:
                default_value = config[config_name]
            try:
                config[config_name] = convert_fct(default_value)
            except:
                msg = ("The configuration value '%s' could not be converted "
                       "to '%s'") % (config_name, str(convert_fct))
                raise ValueError(msg)

        # Call the write function. The write function is supposed to raise the
        # appropriate error in case anything is amiss.
        input_files = writer["function"](config=config, events=_events,
                                         stations=_stations)

        # If an output directory is given, it will be used.
        if output_dir:
            # Create the folder if it does not exist.
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.isdir(output_dir):
                msg = "output_dir %s is not a directory" % output_dir
                raise ValueError(msg)
            output_dir = os.path.abspath(output_dir)

            # Now loop over all files stored in the dictionary and write them.
            for filename, content in input_files.iteritems():
                with open(os.path.join(output_dir, filename), "wt") \
                        as open_file:
                    open_file.write(content)

        return input_files

    def __find_write_scripts(self):
        """
        Helper method to find all available writer scripts. A write script is
        defined as being in the folder "writer" and having a name of the form
        "write_XXX.py". It furthermore needs to have a write() method.
        """
        # Most generic way to get the 'backends' subdirectory.
        write_dir = os.path.join(os.path.dirname(inspect.getfile(
            inspect.currentframe())), "backends")
        files = glob.glob(os.path.join(write_dir, "write_*.py"))
        import_names = [os.path.splitext(os.path.basename(_i))[0]
                        for _i in files]
        write_functions = {}
        for name in import_names:
            module_name = "backends.%s" % name
            try:
                module = __import__(
                    module_name, globals(), locals(),
                    ["write", "REQUIRED_CONFIGURATION",
                     "DEFAULT_CONFIGURATION"], -1)
                function = module.write
                required_config = module.REQUIRED_CONFIGURATION
                default_config = module.DEFAULT_CONFIGURATION
            except Exception as e:
                print("Warning: Could not import %s." % module_name)
                print("\t%s: %s" % (e.__class__.__name__, str(e)))
                continue
            if not hasattr(function, "__call__"):
                msg = "Warning: write in %s is not a function." % module_name
                print(msg)
                continue
            # Append the function and some more parameters.
            write_functions[name[6:]] = {
                "function": function,
                "required_config": required_config,
                "default_config": default_config}

        self.__write_functions = write_functions

    def get_available_formats(self):
        """
        Get a list of all available formats.
        """
        self.__find_write_scripts()
        return list(self.__write_functions.keys())

    def get_config_params(self, solver_name):
        self.__find_write_scripts()
        if solver_name not in self.__write_functions.keys():
            msg = "Solver '%s' not found." % solver_name
            raise ValueError(msg)
        writer = self.__write_functions[solver_name]

        return writer["required_config"], writer["default_config"]

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
        if None in (origin.latitude, origin.longitude, origin.depth,
                    origin.time):
            msg = ("Every event origin needs to have latitude, longitude, "
                   "depth and time")
            raise ValueError(msg)
        # The focal mechanism of course needs to have a moment tensor.
        if not foc_mec.moment_tensor or not foc_mec.moment_tensor.tensor:
            msg = "Every event needs to have a moment tensor."
            raise ValueError(msg)
        # Also all six components need to be specified.
        mt = foc_mec.moment_tensor.tensor
        if None in (mt.m_rr, mt.m_tt, mt.m_pp, mt.m_rt, mt.m_rp, mt.m_tp):
            msg = "Every event needs all six moment tensor components."
            raise ValueError(msg)

        # Extract event descriptions.
        if event.event_descriptions:
            description = ", ".join(i.text for i in event.event_descriptions)
        else:
            description = None

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
            "m_tp": mt.m_tp,
            "_event_id": event.resource_id.resource_id,
            "description": description})
