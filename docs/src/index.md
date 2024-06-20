# Verifying Hardware with Vertex

_Vertex_ is a simulation-based functional verification framework for digital hardware designs. 

Vertex leverages _file I/O_ and _software programming languages_ to verify hardware designs in their native hardware description language.

The verifying hardware with Vertex is separated into 3 steps: 

1. Model the hardware design in software to generate input vectors and expected output vectors

2. Simulate the hardware design by sending input vectors to the design under test, receiving output vectors from the design under test, and logging comparisons between simulated output vectors and expected output vectors

3. Analyze the logged comparisons for any errors

## Sections
The following documentation will be mainly divided into 4 sections:
1. [Tutorials](./tutorials/tutorials.md) - Step-by-step lessons using Vertex
2. [User Guide](./user/user.md) - General procedures for "how-to" solve common problems
3. [Topic Guide](./topic/topic.md) - Explanations that clarify and provide more detail to particular topics
4. [Reference](./reference/reference.md) - Technical information

## About the Project
The project is open-source under the MIT license and is available on [GitHub](https://github.com/cdotrus/vertex).

## About the Documentation
Documentation system and methodology is inspired by [Divio](https://documentation.divio.com).
