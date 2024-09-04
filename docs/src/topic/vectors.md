# Test Vectors

One of the key concepts in the Verb framework is using _file I/O_ to communicate data between the software model and the hardware design throughout the verification process. When running the hardware simulation, the testbench receives the information about the inputs and expected outputs by reading files called _vectors_.

_Vectors_ store the test vectors for the hardware design to use- that is, they contain the actual data to either drive as inputs or compare with their outputs.

Typically, the set of input test vectors are written to a file called "inputs.txt", and the set of expected output test vectors are written to a file called "outputs.txt".

## Vectors file format

Each vector is entered on a new line in a vectors file.

A vector uses the following pattern:

```
<port 1 value> <port 2 value> ...
```

Each port value contains a string of 1's and 0's and each port is separated by a single space character. An additional space character follows the final port value.

Example: "inputs.txt"

```
1 0111 0100 
0 1010 1111 
1 1011 1100 
0 0000 1001
```

In this example, we are testing a hardware design that has 3 ports to be driven by the vector file (one port of 1-bit width and two ports of 4-bit width). For this simulation, there are 4 test vectors that will be sent as input to the design over the duration of the simulation.

An empty newline character does not exist at the end of the file. The last line of the file contains the final test vector.

## Details

It is the testbench's responsibility to determine _when_ to actually supply each vector to the hardware design. This approach is taken to provide users with fine-grain control over the timing of the data-flow within the simulation environment.

One of the consequences of having the vectors files have a very simple format allows for easier parsing in the hardware languages. It also means not a lot of additional information is known, such as what order the ports are arranged in each vector.

To check the order of ports that Verb writes to vectors, see the `verb link` command. An option is available to print the list of ports in their vector order for inputs and outputs. 

A user can also find the port order by identifying the order in which the ports appear in the source code for the hardware design's port interface declarations.