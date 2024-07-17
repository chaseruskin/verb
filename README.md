# _Verb_

[![Pipeline](https://github.com/cdotrus/verb/actions/workflows/pipeline.yml/badge.svg?branch=trunk)](https://github.com/cdotrus/verb/actions/workflows/pipeline.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Verb is a framework for simulating digital hardware designs. 

Verb leverages _file I/O_ and _software programming languages_ to simulate hardware designs in their native hardware description language (HDL).

Simulating hardware with Verb is separated into 3 steps:

1. Write a design model in software to generate I/O vector files

2. Simulate the hardware design by sending input vectors to the design under test, receiving output vectors from the design under test, and logging comparisons between simulated output vectors and expected output vectors

3. Analyze the logged comparisons for any failures or errors

Verb can be used for all types of simulation; from simple experimentation to advanced functional verification. Read [Hardware Simulation with Verb](https://cdotrus.github.io/verb/) to learn more about Verb and how to use it in your next hardware project.

## Installing

Verb is available as 3 separate components: a library for software drivers, a library for hardware drivers, and a command-line application for assisting in development as well as running pre-simulation and post-simulation processes.

Any of the components may have one or more implementations; install the component in the programming language or HDL you prefer. See [Installing](https://cdotrus.github.io/verb/starting/installing.html) for more details and available implementations.

If you are using Linux or macOS, you can install all the components (using `pip`, `orbit`, and `cargo`):
```
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/cdotrus/verb/trunk/install.sh | bash -s --
```

## Details

Verb defines a collection of low-level functions, also known as _drivers_, that allow a user to communicate between software models and hardware designs for simulation. The main form of communication Verb uses to pass data between hardware and software is _file I/O_. This method was chosen due to its simplicity and wide support in existing HDLs. Drivers are implemented in both the software programming languages and the HDLs to faciliate the interaction between the design and the model.

By using the drivers available through Verb, for every new hardware design users must only focus on writing the model, not configuring the whole testbench.

This framework attempts to decouple the functional and timing aspects of a hardware simulation. The functional model is written in software, while the exact timing of how to monitor and check the design under test is kept in HDL. This separation of layers allows each language to focus in how they are naturally used.

## Project Goals

The following objectives drive the design choices behind building this framework:

- __ease of use__: Verifying the next design should be intuitive and easy to set up

- __general-purpose__: Be generic and allow the user enough control to support a wide range of designs, from purely combinational logic to control-flow architectures

- __increased productivity__: Using the framework should result in shorter times spent in the verification phase due to reusing highly modular components with insightful results

## Framework

![](./docs/src/images/system.png)

The Verb framework is divided into 3 main layers.

- _Software Layer_: low-level functions to generate inputs and outputs and analyze recorded data
- _Data Layer_: persistent storage of data to be shared between hardware and software layers
- _Hardware Layer_: low-level functions to load inputs and outputs, drive inputs, check outputs, and log events

This separation of functionality is important for modularity. If a model needs to be written in a different language (Python/C++/Rust), then only the software layer requires changes; the data layer and hardware layer are left unmodified. Having well-defined interfaces between these layers allows for the framework to easily expand to new software languages and HDLs.

See [Overview](https://cdotrus.github.io/verb/topic/overview.html) for more information about how the framework works.

## Key Features

Some notable features include:

- Fine-grain control over when to send inputs and check outputs, produce inputs or outputs cycle-by-cycle or wait on particular control signals

- Ability to enable coverage-driven test generation to help minimize the number of tests required to achieve a target coverage

- Supported coverage nets: `CoverPoint`, `CoverRange`, `CoverGroup`, `CoverCross`

- Ability to generate HDL glue-logic code per design-under-test to connect hardware drivers layer to the data layer

## Workflow 

Verification is done through simulation at the hardware level. The hardware simulation is trace-based; the set of inputs and outputs are pre-recorded before the simulation begins. These traces are stored in the data layer.

The workflow is broken down into 3 main steps:

1. Run the software model using Verb software drivers to write files at the data layer for design under test's inputs and expected outputs based on defined coverage.

2. Run hardware simulation to send inputs and receive outputs and record outcomes into a log file using Verb hardware drivers.

3. Run the binary (`verb check`) to interpret/analyze outcomes stored in log file. If all tests passed, then the program exits with code `0`. If any tests failed, then the program exits with code `101`.

When the software model is generating tests, it can also keep track of what test cases are being covered by using _coverage nets_, such as `CoverGroups` or `CoverPoints`. By handling coverages in software, it allows for coverage-driven test generation (CDTG) by choosing the next set of inputs that will work toward achieving total coverage.

Once the test files are generated at the data layer, the simulation can begin in the hardware description language. At the hardware drivers layer, a package of functions exist for clock generation, system reseting, signal driving, signal montioring, and logging.

## Related Works

- [cocotb](https://www.cocotb.org): coroutine based cosimulation testbench environment for verifying VHDL and SystemVerilog RTL using Python