## Waveform Solver Input File Generator

[![Build Status](https://travis-ci.org/krischer/wfs_input_generator.png?branch=master)](https://travis-ci.org/krischer/wfs_input_generator)

Seismic waveform solvers are generally written in a high-performance language
and are controlled with the help of carefully crafted input files. These
input files are very solver dependent and have their own quirks. This module
attempts to create a generic input file generator that hides the actual input
files' syntax and has a usable Python API.

From a high-level point of view the solvers require three distinct types of
input: the sources, the receivers, and the detailed configuration of the
solver which includes all the remaining parts like time-stepping, the domain
setup, which type of simulation to perform, and many more.

The `wfs_input_generator` is able to extract the list of sources or seimic
events and the list of receivers or seismic stations from various common
formats that are readily available. It also help with the solver specific
configuration, other then the input file formatting, by dividing the
configuration values in a (hopefully) small set of required parameters and
a larger list of optional ones with sensible default values.

A main focus of the development is to make it as easy as possible to add
support for further waveform solver input file formats. This is achieved
by employing a system of of simple backends; one for each supported solver.

The following sketch shows a short overview of the module's working:

![Flow](https://raw.github.com/krischer/wfs_input_generator/master/misc/wfs_input_gen_flow.png)


## Dependencies and Installation

The module is written in pure Python and thus only has very minimal
dependencies. It currently only works with Python 2.7.x as ObsPy does not yet
support Python 3.x.

### Requirements

* Python 2.7.x
* ObsPy >= 0.8.3

#### Additional requirements for running the test suite:

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

The input file generation is steered with a Python scrupt.

The first step it to create an `InputFileGenerator` object.

```python
from wfs_input_generator import InputFileGenerator
gen = InputFileGenerator()
```

This object requires seismic events, which act as the sources, seismic stations,
which act as the receivers and finally some solver specific configuration to be
able to eventually generate input files for different solvers.

The events and stations can be the same for every solver, but the rest of the
configuration cannot be unified; the different solvers simply require very
different parameters.


### Adding Events

Events or seismic sources are added with the help of the `add_events()`
method. Different formats are supported. The function can be called as often as
necessary to add as many events as desired. Duplicates will be automatically
discarded.

Many solvers are only able to accept a single event and thus will raise an
error upon input file creation if multiple events are present.

Different ways to add one or more events are demonstrated by example:

```python
# Add one or more QuakeML files.
gen.add_events("quake.xml")
gen.add_events(["path/to/quake1.xml", "path/to/quake2.xml"])

# Add a QuakeML with a URL to a webservice.
gen.add_events("http://earthquakes.gov/quakeml?parameters=all")

# Directly add an event as a dictionary.
gen.add_events({
    "latitude": 45.0,
    "longitude": 12.1,
    "depth_in_km": 13.0,
    "origin_time":
        obspy.UTCDateTime(2012, 4, 12, 7, 15, 48, 500000),
    "m_rr": -2.11e+18,
    "m_tt": -4.22e+19,
    "m_pp": 4.43e+19,
    "m_rt": -9.35e+18,
    "m_rp": -8.38e+18,
    "m_tp": -6.44e+18})
gen.add_events([{...}, {...}, ...])

# JSON also works. Either as a single JSON object as a JSON arrays of objects.
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

# Webservices serving StationXML or (X)SEED work by
# simply providing the URL.
gen.add_stations("http://fdsn_webservice.org/...")

# There is also legacy support for coordinates
# embedded into SAC files.
gen.add_stations("station7.sac")
gen.add_stations(["station8.sac", "station9.sac"])

# Furthermore Python dictionaries are fine. The id is
# a simple string but for many purposes it should be
# NETWORK_ID.STATION_ID as defined in the SEED manual.
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

Events and stations can be filtered. This is useful for using the same
(potentially very large) StationXML and QuakeML files for many simulations.
Provide a different filter for each run restricting the existing dataset.

Filters are defined as positive filters, thus they describe what should be the
content of the input files and not what should be neglected.

You can set and change the filters at any time during the setup process. They
are applied at input file creation time.

#### Event Filters

Event filters are only useful for QuakeML input as they depend on the public id
of an event. They are simply a list of one ore more event ids.

```python
gen.event_filter = ["smi:local/event_id_1", "smi:/local_event_id_2"]

# A JSON array also works.
gen.event_filter = '["smi:local/event_id_1", "smi:/local_event_id_2"]'
```

#### Stations Filters

Station filters are a list of station ids. UNIX style wildcards are supported.

```python
gen.station_filter = ["BW.FURT", "TA.A*", "TA.Y?H"]

# Again JSON arrays are just as fine.
gen.station_filter = '["BW.FURT", "TA.A*", "TA.Y?H"]'
```

### Solver Specific Configuration

The rest of the configuration is unfortunately very solver dependent. The inputs
they require are too different to make it feasible to extract a common subset.

If needed the supported output formats of the module can be queried

```python
>>> # Get a list of available formats.
>>> gen.get_available_formats()
>>> ['ses3d_4_0', 'SPECFEM3D_CARTESIAN']
```

The configuration parameters for each supported solver can be requested with

```python
>>> required, optional = gen.get_config_params('ses3d_4_0')
>>> # Required are the parameters one absolutely has to set.
>>> # It is a dictionary with the key being the parameter name
>>> # and the value a tuple of type and description.
>>> required.items()[0]
('mesh_max_longitude', (float, 'The maximum longitude of the mesh'))
>>> # Optional will have sensible default values.
>>> # It is again a dictionary but this time the value is three-tuple
>>> # of default value, type, and description.
>>> optional.items()[0]
('adjoint_forward_sampling_rate', (15, int, 'The sampling...')
```

Once the necessary parameters are known they can be set in a couple of
different ways. The required parameters must be set before a file can be
written, otherwise an error will be raises. If no value is given for an
optional parameter, it's default value will be used.

```python
# Directly attach attributes to the config object.
gen.config.time_stepping = 5.5

# Set values from a dictionary.
get.add_configuration({'some_value': 2,
                       'other_value': 2})

# From a JSON string containing a single object.
get.add_configuration('{"some_value":2, ...}')
```

The last step is to actually write the input files. Per default it will
return a dictionary with the keys being the filenames and the values
being the file contents.

```python
>>> output = get.write(format="ses3d_4_0")
>>> output.keys()
['stf', 'relax', 'setup', 'event_list', 'event_1', 'recfile_1']

# One can also directly write the files to a specified folder.
gen.write(format="ses3d_4_0", output_dir="solver_input_files")
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
