## Waveform Solver Input File Generator

[![Build Status](https://travis-ci.org/krischer/wfs_input_generator.png?branch=master)](https://travis-ci.org/krischer/wfs_input_generator)

Seismic waveform solvers are generally written in a high-performance language
and require carefully crafted input files to work.  These input files are very
solver dependent and have their own quirks.  This module attempts to create a
generic input file generator that hides the actual input files' syntax and is
steered with a usable Python API.

It is most useful for performing simulations of real earthquakes. The module
reads the necessary information from several file formats commonly in use in
the field.

A main focus of the development is to make it as easy as possible to add
support for further waveform solver input file formats. This is described later
on in more detail.

The following sketch shows a short overview of what this module does:

![Flow](https://raw.github.com/krischer/wfs_input_generator/master/misc/wfs_input_gen_flow.png)


## Dependencies and Installation

The module is written in 100 % Python and thus only has very minimal
dependencies. It currently only works with Python 2.7.x as ObsPy does not yet
support Python 3.x.

### Requirements

* Python 2.7.x
* ObsPy >= 0.8.3

#### Additional requirements for running the test suite

* pytest
* flake8 >= 2.0
* mock

### Installation

#### User Installation

To install the most recent version, make sure ObsPy is installed and execute

```bash
$ pip install https://github.com/krischer/wfs_input_generator/archive/master.zip
```

To also install the requirements for the tests, run

```bash
$ pip install https://github.com/krischer/wfs_input_generator/archive/master.zip[tests]
```

#### Developer Installation

If you want to develop your own backends for writing input files for other
solver you have to install the wfs_input_generator with in-place installation.

```bash
git clone https://github.com/krischer/wfs_input_generator.git
cd wfs_input_generator
pip install -v -e .[tests]
```

## Usage

A short Python script is necessary to steer the input file generation.

The first step it to create an `InputFileGenerator` object.

```python
from wfs_input_generator import InputFileGenerator
gen = InputFileGenerator()
```

The object requires seismic events, which act as the sources, seismic stations,
which act as the receivers and finally some solver specific configuration to be
able to eventually generate input files for different solvers.

The events and stations can be the same for every solver, but the rest of the
configuration cannot be unified; the different solvers are simply require very
different parameters.


### Adding Events

Events or seismic sources are added with the help of the `add\_events()`
method. Different formats are supported. The function can be called as often as
necessary to add as many events as desired. Duplicates will be automatically
discarded.

Many solvers are only able to accept a single event and thus will raise an
error upon input file creation if multiple events are present.


```python
# Add a QuakeML files.
gen.add_events("quake.xml")
gen.add_events(["path/to/quake1.xml", "path/to/quake2.xml"])

# Add a QuakeML with a URL to a webservice.
gen.add_events("http://earthquakes.gov/quakeml?parameters=all")

# Directly add an event as a dictionary.
gen.add_events({
    "latitude": 45.0,
    "longitude": 12.1,
    "depth_in_km": 13.0,
    "origin_time": obspy.UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
    "m_rr": -2.11e+18,
    "m_tt": -4.22e+19,
    "m_pp": 4.43e+19,
    "m_rt": -9.35e+18,
    "m_rp": -8.38e+18,
    "m_tp": -6.44e+18})
gen.add_events([{...}, {...}, ...])

# JSON also works. Either as a single JSON object as are JSON arrays of objects.
json_str = """
{
    "latitude": 45.0,
    "longitude": 12.1,
    "depth_in_km": 13.0,
    "origin_time": "2012-04-12T07:15:48.500000Z",
    "m_rr": -2.11e+18,
    "m_tt": -4.22e+19,
    "m_pp": 4.43e+19,
    "m_rt": -9.35e+18,
    "m_rp": -8.38e+18,
    "m_tp": -6.44e+18
}
"""
gen.add_events(json_string)

json_str = """
[{...}, {...}]]
"""
gen.add_events(json_str)
```


### Adding Stations

The stations will act as the receivers during the simulation. Again, the most
common formats are supported to facilitate integration into existing workflows.

```python
# Add one or more (X)SEED files.
gen.add_stations("station1.seed")
gen.add_stations(["station2.seed", "station3_xseed.xml"])

# StationXML works just fine.
gen.add_stations("station4.xml")
gen.add_stations(["station5.ml", "station6.xml"])

# Webservices serving StationXML or (X)SEED work by simply providing the URL.
gen.add_stations("http://fdsn_webservice.org/...")

# There is also legacy support for coordinates embedded into SAC files.
gen.add_stations("station7.sac")
gen.add_stations(["station8.sac", "station9.sac"])

# Furthermore Python dictionaries are fine.
gen.add_stations({
    "id": "BW.FURT",
    "latitude": 48.162899,
    "longitude": 11.2752,
    "elevation_in_m": 565.0,
    "local_depth_in_m": 10.0})
gen.add_stations([{...}, {...}, ...])

# As are JSON objects and arrays of objects.
json_str = """
{
    "id": "BW.FURT",
    "latitude": 48.162899,
    "longitude": 11.2752,
    "elevation_in_m": 565.0,
    "local_depth_in_m": 10.0})
}
"""
gen.add_stations(json_str)

json_str = """
[{...}, {...}, ...]
"""
gen.add_stations(json_str)
```

### Event and Station Filters

Events and stations can furthermore be filtered. This is useful for using the
same (potentially very large) StationXML and QuakeML files for many
simulations. Simply provide a different filter for each run restricting the
existing dataset.

Filters are defined as positive filters, thus they describe what should be the
content of the input files and not what should be neglected.

You can set and change the filters at any time during the setup process. They
are applied at input file creation time.

#### Event Filters

Event filters are only useful for QuakeML input as they depend on the public id
of an event. They are simply a list of event ids.

```python
get.event_filter = ["smi:local/event_id_1", "smi:/local_event_id_2"]

# A JSON array also works.
get.event_filter = '["smi:local/event_id_1", "smi:/local_event_id_2"]'
```

#### Stations Filters

Station filters are a list of station ids, consisting of the network id,
a dot, and the station id. UNIX style wildcards are supported.

```python
get.station_filter = ["BW.FURT", "TA.A*", "TA.Y?H"]

# Again JSON arrays are just as fine.
get.station_filter = '["BW.FURT", "TA.A*", "TA.Y?H"]'
```

### Solver Specific Configuration

```python
# Add some solver specific documentation.
gen.config.time_stepping = 5.5

# Get a list of available output format
gen.get_available_formats()
['ses3d_4_0', 'ses3d_muc_svnr276']

# Write the input files to a specified folder.
gen.write(format="ses3d_svnr276", output_dir="solver_input_files")
```

## How to add support for a new solver
Adding support for a new solver is simply a matter of adding a new python
script. The input file generator main class will take care of finding it and
calling it.

Put the file in the `wfs_input_generator/writers` subdirectory. It has to have
the name `write_SOLVER.py` where `SOLVER` shoud be a very accurate description
of the used solver.

The file has to contain a function akin to the following:

```python
def write(config, events, stations, output_directory):
    # Logic here
```

It will be called by the `InputFileGenerator.write()` method if the
corresponding format has been requested.

The write function has to accept four arguments in the given order.

### The config argument
The config argument is a `obspy.core.AttribDict` instance and contains any user
specfied configuration values.

### The events argument
It is a list of dictionaries. You can be sure they have the following format:

```python
{"latitude": 28.7,
 "longitude": -113.1,
 "depth_in_km": 13.0,
 "origin_time": UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
 "m_rr": -2.11e+18,
 "m_tt": -4.22e+19,
 "m_pp": 4.43e+19,
 "m_rt": -9.35e+18,
 "m_rp": -8.38e+18,
 "m_tp": -6.44e+18}
```
The `origin_time` value will be an `obspy.UTCDateTime` instance, the rest
ordinary floats.

### The stations argument
It is a list of dictionaries. You can be sure they have the following format:

```python
{"id": "BW.FURT",
 "latitude": 48.162899,
 "longitude": 11.2752,
 "elevation_in_m": 565.0,
 "local_depth_in_m": 0.0},
```

The `id` value will be a string and all other values will be floats.

### The output_directory argument
This is a string containing the directory where all files should be written to.
You can be sure that the directory exists. Please create filenames in the following way to ensure cross-platform compatibility:

```python
path = os.path.join(output_directory, "new_file.txt")
```

This will generate the absolute path of the `new_file.txt` file in the output_directory.
