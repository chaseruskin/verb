-- Project: Verb
-- Package: tutils
--
-- Provides test utility functions for testbench simulation. This involves
-- reading interface signals, loading expected values, and various 
-- simulation-specific tasks.

library ieee;
use ieee.std_logic_1164.all;

library amp;
use amp.types.all;
use amp.cast.all;

library std;
use std.textio.all;

package tutils is

  -- Generates a half duty cycle clock `clk` with a period of `period` that
  -- is continuously driven until `halt` is set to true. 
  procedure spin_clock(signal clk: out logic; period: time; signal halt: bool);

  -- Asynchronously triggers the logic bit `datum` to its state `active` and then 
  -- asynchronously deactivates the bit to its initial value after `cycles`
  -- clock cycles elapse.
  --
  -- The trigger will not be applied if `cycles` is set to 0. The signal will
  -- deactivate on the falling edge of the `cycles` count clock cycle.
  procedure trigger_async(signal clk: logic; signal datum: inout logic; constant active: logic; cycles: usize);

  -- Synchronously triggers the logic bit `datum` to its state `active` and then 
  -- asynchronously deactivates the bit to its initial value after `cycles`
  -- clock cycles elapse.
  --
  -- The trigger will not be applied if `cycles` is set to 0. The signal will
  -- deactivate on the falling edge of the `cycles` count clock cycle.
  procedure trigger_sync(signal clk: logic; signal datum: inout logic; constant active: logic; cycles: usize);

  -- Drive a logic vector signal `x` with a value from the line `row`.
  procedure drive(variable row: inout line; signal x: out logics);

  -- Drive a logic bit signal `x` with a value from the line `row`.
  procedure drive(variable row: inout line; signal x: out logic);

  -- Read a logic vector value from the line `row` into the variable `x`.
  procedure load(variable row: inout line; variable x: out logics);

  -- Read a logic bit value from the line `row` into the variable `x`.
  procedure load(variable row: inout line; variable x: out logic);
  
  -- Sets `halt` to true and enters an infinite wait statement to signal 
  -- that the simulation is complete.
  procedure complete(signal halt: out bool);

  -- Enters an infinite wait if the `halt` signal is set to true.
  procedure check(halt: in bool);

end package;


package body tutils is

  procedure complete(signal halt: out bool) is
  begin
    halt <= true;
    wait;
  end procedure;

  procedure check(halt: in bool) is
  begin
    if halt = true then 
      wait;
    end if;
  end procedure;

  procedure spin_clock(signal clk: out logic; period: time; signal halt: bool) is
    variable inner_clk : logic := '0';
  begin
    while halt = false loop
      clk <= inner_clk;
      wait for period/2;
      inner_clk := not inner_clk;
    end loop;
    wait;
  end procedure;

  procedure trigger_async(signal clk: logic; signal datum: inout logic; constant active: logic; cycles: usize) is
    variable prev_datum: logic;
  begin
    if datum = 'U' then
      assert false report "TUTILS.TRIGGER_ASYNC: signal's current value is 'U'" severity warning;
    end if;
    prev_datum := datum;
    -- only apply the trigger if the number of cycles to delay is greater than zero
    if cycles > 0 then
      wait until falling_edge(clk);
      datum <= active;
      wait for 0 ns;
      for i in 1 to cycles loop
        wait until rising_edge(clk);
      end loop;
      wait until falling_edge(clk);
      datum <= prev_datum;
    end if;
    -- wait for 0 ns;
  end procedure;

  procedure trigger_sync(signal clk: logic; signal datum: inout logic; constant active: logic; cycles: usize) is
    variable prev_datum: logic;
  begin
    if datum = 'U' then
      assert false report "TUTILS.TRIGGER_SYNC: signal's current value is 'U'" severity warning;
    end if;
    prev_datum := datum;
    -- only apply the trigger if the number of cycles to delay is greater than zero
    if cycles > 0 then
      wait until rising_edge(clk);
      datum <= active;
      wait for 0 ns;
      for delay in 1 to cycles loop
        wait until rising_edge(clk);
      end loop;
      wait until falling_edge(clk);
      datum <= prev_datum;
    end if;
    -- wait for 0 ns;
  end procedure;

  procedure drive(variable row: inout line; signal x: out logics) is
    variable word: str(1 to x'length);
    variable temp: logics(x'range) := (others => '0');
    variable delim: char;
    variable j: psize := 1;
  begin
    if row'length > 0 then
      read(row, word);
      for i in x'range loop
        temp(i) := to_logic(word(j));
        j := j + 1;
      end loop;
      x <= temp;
      -- ignore the delimiter
      read(row, delim);
      -- wait for 0 ns;
    end if;
  end procedure;

  procedure load(variable row: inout line; variable x: out logics) is
    variable word: str(1 to x'length);
    variable delim: char;
    variable j: psize := 1;
  begin
    if row'length > 0 then
      read(row, word);
      for i in x'range loop
        x(i) := to_logic(word(j));
        j := j + 1;
      end loop;
      -- ignore the delimiter
      read(row, delim);
    end if;
  end procedure;

  procedure drive(variable row: inout line; signal x: out logic) is
    variable word: char;
    variable delim: char;
  begin
    if row'length > 0 then
      read(row, word);
      x <= to_logic(word);
      -- ignore the delimiter
      read(row, delim);
      -- wait for 0 ns;
    end if;
  end procedure;

  procedure load(variable row: inout line; variable x: out logic) is
      variable word: char;
      variable delim: char;
  begin
    if row'length > 0 then
      read(row, word);
      x := to_logic(word);
      -- ignore the delimiter
      read(row, delim);
    end if;
  end procedure;

end package body;