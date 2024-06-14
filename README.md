# _Vertex_

Vertex is a simulation-based functional verification framework for digital hardware designs.

The framework can be divided into 3 major actions: 

1. Model the hardware design in software to generate input vectors and expected output vectors.
2. Simulate the hardware design by sending input vectors to the design under test and logging comparisons between simulated output vectors and expected output vectors.
3. Analyze the logged events for any errors.

## Install

### Software

The framework is available as a library (for helping model hardware behavior) as well as a binary (for running actions in the verification process).

For the Python library, run the following Pip command:
```
pip install git+"https://github.com/cdotrus/vertex.git@stable#egg=vertex"
```

For the binary, run the following Cargo command:
```
cargo install --git https://github.com/cdotrus/vertex --branch stable
```

### Hardware

The framework is available as a library (for helping create testbenches).

For the VHDL library, run the following Orbit command:
```
orbit install vertex:latest --url "https://github.com/cdotrus/vertex/archive/refs/heads/stable.zip"
```

## Motivation

Verification is an important process in the hardware development cycle that ensures a design functions as intended and is free of bugs. As a design increases in complexity, the number of coding errors also increases. Therefore, one approach to verifying a logic design conforms to specification is _functional verification_, where tests are performed to check if the design does what is intended under a set of conditions. However, designs typically have an insurmountable amount of test cases to create and perform each one. Therefore, producing test cases and determining when enough test cases is "enough" requires a well-designed and efficient approach.

Any hardware design can be translated behaviorally to software, and by writing the model in software, it provides an extra level of cross-checking to ensure the hardware design matches specification. Writing the model in software is also typically easier with nicer language constructs and an abundance of existing libraries available. With Vertex, all of the plumbing in setting up tests is minimized so testing the next hardware design only requires focusing on writing the model, not the whole framework.

Vertex is a collection of functions that help generate, store, load, and analyze test cases. The functions are implemented in both software and hardware description languages (HDL) to facilitate the interaction between the framework's layers of abstraction. These functions allow the user largely focus on only two components when performing functional verification: the software model and the hardware design.

This framework attempts to decouple the functional and timing aspects of a hardware simulation. The functional model is written in software, while the exact timing of how to monitor and check the design under test is kept in HDL. This separation of layers allows each language to excel at what it is good at.

## Project Goals

The following objectives drive the design choices behind building this framework:
- __ease of use__: Verifying the next design should be easy to set up and configure
- __general-purpose__: Be generic and allow the user enough control to support a wide range of designs, from purely combinational logic to control-flow architectures
- __increased productivity__: Using the framework should result in shorter times spent in the verification phase due to reusing highly modular components and insightful results

## Architecture

![](./docs/src/images/system.png)

The Vertex framework is divided into three main layers.

- _Software Layer_: low-level functions to generate inputs and outputs and analyze recorded data
- _Data Layer_: persistent storage of data to be shared between hardware and software layers
- _Hardware Layer_: low-level functions to load inputs and outputs, drive inputs, check outputs, and log events

This separation of functionality is important for modularity. If a model needs to be written in a different language (Python/C++/Rust), then only the software layer requires changes; the data layer and hardware layer are left unmodified. Having well-defined interfaces between these layers allows for the framework to easily expand to new software languages and HDLs.


### Software Layer

The software layer implements the low-level functions required to run any form of test. It translates your test cases into the data layer represented by a specific file format.

The software layer is responsible for generating test inputs, tracking coverage, and generating test outputs. When defining signals in your software model, you can also specify their probability distribution to randomly sample based on distributions. If not specified, the default is uniform distribution.

The software layer can also generate HDL code, which can be directly copied into the testbench for establishing connections between the hardware design and the data layer.

The software layer is available as a library and as a stand-alone program.

### Data Layer

The data layer stores the tests to run during simulation and the expected outputs. This information is typically stored in a specific file format already handled by Vertex.

Each line in a data file is a _transaction_. A transaction in this sense is the combination of complete set of inputs or outputs. For data stored in an input file, each transaction is to be the input into the design-under-test on a single clock cycle. For data stored in an output file, each transaction is the outputs to be checked against the design-under-test's outputs in the scoreboard. The output transactions do not have to be checked every clock cycle, and may only be cared when a certain condition occurs (such as a valid signal being asserted).

The number of transactions stored as inputs and outputs does not have to be 1-to-1. There may be more input transactions (fed every clock cycle) than output transactions (only checked when valid).

### Hardware Layer

The hardware drivers implement the low-level functions required to receive data from the data layer. This data is read during simulation to run test cases and automatically assert outputs.

The hardware layer is responsible for the timing of the simulation: specifically determining when to drive inputs and monitoring when to check outputs.

## Key Features

- Fine-grain control over when to send inputs and check outputs, produce inputs or outputs cycle-by-cycle or wait on particular control signals
- Ability to enable coverage-driven test generation (CDTG) to help minimize the number of tests required to achieve the target coverage
- Supported coverage nets: `CoverPoint`, `CoverRange`, `CoverGroup`, `CoverCross`
- Ability to generate HDL glue-logic code per design-under-test to connect hardware drivers layer to the data layer

## Operation 

Verification is done through simulation at the hardware level. The hardware simulation is trace-based; the set of inputs and outputs are pre-recorded before the simulation begins. These traces are stored in the data layer.

The workflow is broken down into 3 main steps:

1. Run the software model using Vertex software drivers to write files at the data layer for design under test's inputs and expected outputs based on defined coverage.

2. Run hardware simulation to send inputs and receive outputs and record outcomes into a log file using Vertex hardware drivers.

3. Run the binary (`vertex check`) to interpret/analyze outcomes stored in log file. If all tests passed, then the program exits with code `0`. If any tests failed, then the program exits with code `101`.

When the software model is generating tests, it can also keep track of what test cases are being covered by using _coverage nets_, such as `CoverGroups` or `CoverPoints`. By handling coverages in software, it allows for coverage-driven test generation (CDTG) by choosing the next set of inputs that will work toward achieving total coverage.

Once the test files are generated at the data layer, the simulation can begin in the hardware description language. At the hardware drivers layer, a package of functions exist for clock generation, system reseting, signal driving, signal montioring, and logging.

## Related Works

- [cocotb](https://www.cocotb.org): coroutine based cosimulation testbench environment for verifying VHDL and SystemVerilog RTL using Python


## References

- https://en.wikipedia.org/wiki/Functional_verification