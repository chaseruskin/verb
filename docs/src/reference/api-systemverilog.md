# SystemVerilog API

Reference documentation for the Verb conjugations in SystemVerilog.

## Package `godan`
[source](https://github.com/chaseruskin/verb/blob/trunk/src/lib/hdl/src/godan.sv)

### Typedefs
`[Verilog] typedef enum {TRACE, DEBUG, INFO, WARN, ERROR, FATAL} tone`

The log level type.


<br>

### Functions
`[Verilog] function automatic int start(input string name)`

Creates the file with the given `name` to prepare for simulation logging.


<br>

`[Verilog] function string parse(inout string row)`

Return a string in binary format by reading a logic value from the line `row`.


<br>

### Tasks
`[Verilog] task finish(int n=0)`

Closes the event log file and ends the simulation completely.


<br>

`[Verilog] task automatic async_on_sync_off(ref logic clk, ref logic pin, input logic active, input int cycles)`

Asynchronous asserts `pin` and synchronously de-asserts `pin` on the
`cycles`'th clock edge.


<br>

`[Verilog] task automatic sync_on_async_off(ref logic clk, ref logic pin, input logic active, input int cycles)`

Synchronously triggers the logic bit `pin` to its state `active` and then 
asynchronously deactivates the bit to its initial value after `cycles`
clock cycles elapse.
  
The trigger will not be applied if `cycles` is set to 0. The signal will
deactivate on the falling edge of the `cycles` count clock cycle.


<br>

`[Verilog] task automatic sync_hi_async_lo(ref logic clk, ref logic pin, input int cycles)`

Synchronously set `pin` high, then asynchronously set `pin` low.


<br>

`[Verilog] task automatic sync_lo_async_hi(ref logic clk, ref logic pin, input int cycles)`

Synchronously set `pin` low, then asynchronously set `pin` high.


<br>

`[Verilog] task automatic async_hi_sync_lo(ref logic clk, ref logic pin, input int cycles)`

Asynchronously set `pin` high, then synchronously set `pin` low.


<br>

`[Verilog] task automatic async_lo_sync_hi(ref logic clk, ref logic pin, input int cycles)`

Asynchronously set `pin` low, then synchronously set `pin` high.


<br>

`[Verilog] task automatic capture(inout int fd, input tone level, input string topic, input string subject, input string predicate = "")`

Captures an event during simulation and writes the outcome to the file `fd`.
  
The time when the task is called is recorded in the timestamp.


<br>

`[Verilog] task assert_eq(input logic[4095:0] received, input logic[4095:0] expected, input string subject)`

Assertion that checks if two logic words `received` and `expected` are equal to each other.
  
Note: https://stackoverflow.com/questions/67714329/systemverilog-string-variable-as-format-specifier-for-display-write


<br>

`[Verilog] task assert_ne(input logic[4095:0] received, input logic[4095:0] expected, input string subject)`

Assertion that checks if two logic words `received` and `expected` are not equal to each other.


<br>

`[Verilog] task automatic assert_stbl(input bit flag, input logic[4095:0] data, input string subject)`

Assertion that checks that the behavior of `data` is stable while the condition `flag` is true (1'b1).


<br>

`[Verilog] task automatic observe(ref logic clk, ref logic flag, input logic active, input int cycles, input string subject)`

Checks the logic `flag` is true (1'b1) on the rising edge of `clk` before `cycles` clock cycles elapse.


<br>

