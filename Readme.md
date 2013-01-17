## Installation

### Requirements:
    * ObsPy >= 0.8

### Installation

Checkout the repository.

```bash
git clone https://github.com/krischer/wfs_input_generator.git
cd wfs_input_generator
```

The recommended way to install the waveform solver input file generator is via
a develop install. This means that you are still able to edit the code and add
new generators.

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

# Add an event
>>> gen.add_events("quake.xml")

# Add some stations
>>> gen.add_stations(["station1.seed", "station2.seed"])

```

## How to add support for a new solver.
Adding support for a new solver is simply a matter of adding one file per
solver.
