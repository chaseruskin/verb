# Installing

Vertex comes in three separate components: a library for software drivers, a library for hardware drivers, and a command-line application for development as well as running pre-simulation and post-simulation processes.

Any of the components may have one or more implementations; install the component in the programming language or HDL you prefer.

## Software library

The software library provides the driver-level code for writing models.

### Python

Using Pip, run the following command:
```
pip install git+"https://github.com/cdotrus/vertex.git@trunk#egg=vertex"
```

## Hardware library

The hardware library provides the driver-level code for creating testbenches.

### VHDL

Using Orbit, run the following command:
```
orbit install vertex --url "https://github.com/cdotrus/vertex/archive/refs/heads/trunk.zip"
```

## Command-line application

The command-line application provides commands for faster development and running pre-simulation and post-simulation processes.

Using Cargo, run the following command:
```
cargo install --git https://github.com/cdotrus/vertex.git
```