# Motivation

Hardware is hard. _Verifying_ hardware, forget about it. Unfortunately, you can't just forget about it.

## Introduction

Verification is an important process in the hardware development cycle that ensures a design functions as intended and is free of bugs. As a design increases in complexity, the number of coding errors also increases. Therefore, one approach to verifying a logic design conforms to specification is _functional verification_, where tests are performed to check if the design does what is intended under a set of conditions. However, designs typically have an insurmountable amount of test cases that make it impractical to create and perform each one. Therefore, producing test cases and determining when enough test cases is "enough" requires a well-designed and efficient approach.

## The problem

Hardware designs are typically described in hardware description languages (HDLs). These are like the software programming languages of the digital hardware space. To test something in HDLs, one may be inclined to continue to use their HDL to write a model (separate from the design itself) and use that to compare how the design functions during a simulation. However, HDLs are not as nice to write software in because, well, they are focused on describing hardware.

Since digital hardware is at least necessary to write software (think about how your computer is built), digital hardware design can be translated behaviorally up the layers of abstraction to software. Therefore, a more natural option to verifying hardware may be to use software programming languages to write the model, and then test it under a simulation enviornment. Writing the model in software is typically easier with nicer language constructs and an abundance of existing libraries readily available. Writing the model in software also provides an extra layer of cross-checking to ensure the hardware design matches the specification. But, how does one integrate any software programming language with any hardware description language to verify a design's behavior?

## The solution

Enter _Vertex_- a functional verification framework for digital hardware designs.

Vertex defines a collection of low-level functions, also known as _drivers_, that allow a user to communicate between software models and hardware designs for verification. The main form of communication Vertex uses to pass data between hardware and software is _file I/O_. This method was chosen due to its simplicity and wide support in existing HDLs. Drivers are implemented in both the software programming languages and the HDLs to faciliate the interaction between the design and the model.

By using the drivers available through Vertex, for every new hardware design users must only focus on writing the model, not configuring the whole testbench.

This framework attempts to decouple the functional and timing aspects of a hardware simulation. The functional model is written in software, while the exact timing of how to monitor and check the design under test is kept in HDL. This separation of layers allows each language to excel at what it is good at.

## Project Goals

The following objectives drive the design choices behind building this framework:

- __ease of use__: Verifying the next design should be intuitive and easy to set up

- __general-purpose__: Be generic and allow the user enough control to support a wide range of designs, from purely combinational logic to control-flow architectures

- __increased productivity__: Using the framework should result in shorter times spent in the verification phase due to reusing highly modular components with insightful results