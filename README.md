# _Verb_

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Verb is a verification library for digital hardware. 

Verb builds on top of [cocotb](https://www.cocotb.org) to provide additional infrastructure for functionally verifying digital hardware designs.

<!-- Verb focuses on functional verification techniques for hardware simulation. Read [Verifying Hardware with Verb](https://chaseruskin.github.io/verb/) (outdated) to learn more about Verb and how to use it in your next hardware project. -->

## Installing

1. Install the repository as a Python package using `pip` (or your favorite Python package manager):
```
pip install git+https://github.com/chaseruskin/verb.git
```

<!-- ## Details

Verb defines a collection of low-level driver functions, also known as _conjugations_, that allow a user to communicate between software models and hardware designs for simulation. The main form of communication Verb uses to pass data between hardware and software is _file I/O_. This method was chosen due to its simplicity and wide support in existing HDLs. Conjugations are implemented in both the software programming languages and the HDLs to faciliate the interaction between the design and the model.

Conjugations are implemented in software and hardware to manage the data transfer across these layers. By using the conjugations available through Verb, for every new hardware design users must only focus on writing the model, not structuring the whole testbench.

This framework attempts to decouple the functional and timing aspects of a hardware simulation. The functional model is written in software, while the exact timing of how to monitor and check the design under test is kept in HDL. This separation of layers allows each language to focus in how they are naturally used. -->

## Project Goals

The following objectives drive the design choices behind building this library:

- __Ease of use__: Verifying the next design should be intuitive and easy to set up

- __General-purpose__: Be generic and allow the user enough control to support a wide range of designs, from purely combinational logic to control-flow architectures

- __Increased productivity__: Using the library should result in shorter times spent in the verification phase due to reusing highly modular components with insightful results

## Key Features

Some notable features include:

- Ability to enable coverage-driven test generation to help minimize the number of tests required to achieve a target coverage

- Supported coverage nets: `CoverPoint`, `CoverRange`, `CoverGroup`, `CoverCross`

<!-- ## Workflow 

Verification is done through simulation at the hardware level. The hardware simulation is trace-based; the set of inputs and outputs are pre-recorded before the simulation begins. These traces are stored in the data layer.

The workflow is broken down into 3 main steps:

1. Run the software model using Verb software drivers to write files at the data layer for design under test's inputs and expected outputs based on defined coverage.

2. Run hardware simulation to send inputs and receive outputs and record outcomes into a log file using Verb hardware drivers.

3. Run the binary (`verb check`) to interpret/analyze outcomes stored in log file. If all tests passed, then the program exits with code `0`. If any tests failed, then the program exits with code `101`.

When the software model is generating tests, it can also keep track of what test cases are being covered by using _coverage nets_, such as `CoverGroups` or `CoverPoints`. By handling coverages in software, it allows for coverage-driven test generation (CDTG) by choosing the next set of inputs that will work toward achieving total coverage.

Once the test files are generated at the data layer, the simulation can begin in the hardware description language. At the hardware drivers layer, a package of functions exist for clock generation, system reseting, signal driving, signal montioring, and logging. -->

## Related Works

- [cocotb](https://www.cocotb.org): coroutine based cosimulation testbench environment for verifying VHDL and SystemVerilog RTL using Python
- [UVM](https://en.wikipedia.org/wiki/Universal_Verification_Methodology): universal verification methodology