## Waveform Solver Input File Generator

[![Build Status](https://travis-ci.org/krischer/wfs_input_generator.png?branch=master)](https://travis-ci.org/krischer/wfs_input_generator)

Seismic waveform solvers are generally written in a high-performance language and
require carefully crafted input files to work.
These input files are very solver dependent and have their own quirks.
This module attempts to create a generic input file generator that hides the actual
input files' syntax and is steered with a nice Python API.

It is most useful for performing simulations of real earthquakes. The module reads
QuakeML and SEED files and derives the necessary information from them. Instead
of reading from QuakeML and SEED files, the necessary information can also be given
as Python dictionaries.

A main focus of the development is to make it as easy as possible to add support for
further input file formats. This is described later on in more detail.

## Installation

### Requirements:
    * ObsPy >= 0.8.3
    * flake8 >= 2.0 (only for running the tests)

### Installation

Checkout the repository.

```bash
git clone https://github.com/krischer/wfs_input_generator.git
cd wfs_input_generator
```

The recommended way to install the waveform solver input file generator is via
a developer installation. This means that you are still able to edit the code
and add new generators.

To do this, either use

```bash
python setup.py develop
```

or

```bash
pip install -v -e .
```

Both work fine.

## Usage

```python
>>> from wfs_input_generator import InputFileGenerator
>>> gen = InputFileGenerator()

# Add an event. Only QuakeML with a given moment tensor right now.
>>> gen.add_events("quake.xml")

# Add some stations. SEED/XSEED/SAC
>>> gen.add_stations(["station1.seed", "station2.seed"])

# Add some solver specific documentation.
>>> gen.config.time_stepping = 5.5

# Get a list of available output format
>>> gen.get_available_formats()
['ses3d_4_0', 'ses3d_muc_svnr276']

# Write the input files to a specified folder.
>>> gen.write(format="ses3d_svnr276", output_dir="solver_input_files")
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
