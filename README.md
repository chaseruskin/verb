# Verb

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Verb is a verification library for digital hardware. 

Verb builds on top of [cocotb](https://www.cocotb.org) to provide functional verification techniques for digital hardware. Most notably, Verb allows one to define functional coverage nets and apply adapative coverage-driven test generation (CDG) for fast functional coverage closure.

<!-- Read [Verifying Hardware with Verb](https://chaseruskin.github.io/verb/) (outdated) to learn more about Verb and how to use it in your next hardware project. -->

## Installing

1. Install the repository as a Python package using `pip` (or your favorite Python package manager):
```
pip install git+https://github.com/chaseruskin/verb.git
```

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

- [Adaptive Test Generation for Fast Functional Coverage Closure](https://dvcon-proceedings.org/wp-content/uploads/Adaptive-Test-Generation-for-Fast-Functional-Coverage-Closure-1.pdf): Research paper on an adaptive test generation technique
- [cocotb](https://www.cocotb.org): Coroutine based cosimulation testbench environment for verifying VHDL and SystemVerilog RTL using Python
- [UVM](https://en.wikipedia.org/wiki/Universal_Verification_Methodology): Universal Verification Methodology
