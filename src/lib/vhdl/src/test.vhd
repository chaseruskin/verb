-- Project: Verb
-- Package: test
--
-- This package brings the separate VHDL packages under a single package
-- for more convenient importing. This package is auto-generated; DO NOT EDIT.

library ieee;
use ieee.std_logic_1164.all;

library std;
use std.textio.all;

library amp;
use amp.types.all;
use amp.cast.all;

package test is

  -- The log level type.
  type tone is (TRACE, DEBUG, INFO, WARN, ERROR, FATAL);

  -- Captures an event during simulation and writes the outcome to the file `fd`.
  -- The time when the procedure is called is recorded in the timestamp.
  procedure capture(file fd: text; level: tone; topic: str; subject: str; predicate: str := "");

  -- Asserts that two logic bits `received` and `expected` are equal to each other.
  procedure assert_eq(file fd: text; received: logic; expected: logic; subject: str);

  -- Asserts that two logic vectors `received` and `expected` are equal to each other.
  procedure assert_eq(file fd: text; received: logics; expected: logics; subject: str);

  -- Asserts that two logic bits `received` and `expected` are not equal to each other.
  procedure assert_ne(file fd: text; received: logic; expected: logic; subject: str);

  -- Asserts that two logic vectors `received` and `expected` are not equal to each other.
  procedure assert_ne(file fd: text; received: logics; expected: logics; subject: str);

  -- Checks the logic bit `datum` enters its active state `active` on the rising edge of `clk` before `cycles` clock cycles elapse.
  procedure monitor(file fd: text; signal clk: logic; signal datum: logic; constant active: logic; constant cycles: usize; subject: str);

  -- Checks the logic vector `data` enters its active state `active` on the rising edge of `clk` before `cycles` clock cycles elapse.
  procedure monitor(file fd: text; signal clk: logic; signal data: logics; constant active: logics; constant cycles: usize; subject: str);

  -- Checks the logic bit `datum` does not change value when its indicator `flag` is in the active state `active`.
  procedure stabilize(file fd: text; signal clk: logic; signal datum: logic; signal flag: logic; constant active: logic; subject: str);

  -- Checks the logic vector `data` does not change value when its indicator `flag` is in the active state `active`.
  procedure stabilize(file fd: text; signal clk: logic; signal data: logics; signal flag: logic; constant active: logic; subject: str);

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

package body test is

  procedure capture(file fd: text; level: tone; topic: str; subject: str; predicate: str := "") is
    variable row: line;
    variable topic_filtered: str(topic'range);

    constant TIMESTAMP_SHIFT: psize := 20;
    constant LOGLEVEL_SHIFT: psize := 10;
    constant TOPIC_SHIFT: psize := 15;

    function format_time(moment: str) return str is
      variable formatted: str(1 to moment'length-1) := (others => '0');
      variable delim_index: usize := 0;
    begin
      -- Collect until finding space character
      for i in moment'length downto 1 loop
        if moment(i) = ' ' then
          delim_index := i;
          exit;
        end if;
      end loop;
      
      -- Remove the space from the time stamp
      if delim_index > 0 then
        formatted(1 to delim_index-1) := moment(1 to delim_index-1);
        formatted(delim_index to formatted'length) := moment(delim_index+1 to moment'length);
        return formatted;
      -- Return the raw moment if there was no detected space
      else
        return moment;
      end if;
    end function;

  begin
    -- record the timestamp of when the event occurred
    write(row, format_time(to_str(now)), left, TIMESTAMP_SHIFT);

    -- record the severity of the event
    if level = TRACE then
      write(row, str'("TRACE"), left, LOGLEVEL_SHIFT);
    elsif level = DEBUG then
      write(row, str'("DEBUG"), left, LOGLEVEL_SHIFT);
    elsif level = INFO then
      write(row, str'("INFO"), left, LOGLEVEL_SHIFT);
    elsif level = WARN then
      write(row, str'("WARN"), left, LOGLEVEL_SHIFT);
    elsif level = ERROR then
      write(row, str'("ERROR"), left, LOGLEVEL_SHIFT);
    elsif level = FATAL then
      write(row, str'("FATAL"), left, LOGLEVEL_SHIFT);
    else
      write(row, str'("INFO"), left, LOGLEVEL_SHIFT);
    end if;

    -- record the topic of the event
    -- filter the topic to prevent illegal characters from messing up format
    topic_filtered := topic;
    for ii in topic'range loop
      if topic(ii) = ' ' then
        topic_filtered(ii) := '_';
        assert false report "EVENTS.CAPTURE: converting ' ' to '_' in event topic" severity warning;
      end if;
    end loop;
    write(row, topic_filtered, left, TOPIC_SHIFT);

    -- record the subject of the event
    if subject /= "" then
      write(row, subject);
    end if;

    -- record the information about the event
    if predicate /= "" then
      if subject /= "" then
        write(row, ' ');
      end if;
      write(row, predicate);
    end if;

    writeline(fd, row);
  end procedure;

  procedure assert_eq(file fd: text; received: logic; expected: logic; subject: str) is
  begin
    if received = expected then
      capture(fd, INFO, "ASSERT_EQ", subject, "receives " & to_str(received) & " and expects " & to_str(expected));
    else 
      capture(fd, ERROR, "ASSERT_EQ", subject, "receives " & to_str(received) & " but expects " & to_str(expected));
    end if;
  end procedure;

  procedure assert_eq(file fd: text; received: logics; expected: logics; subject: str) is
  begin
    if received = expected then
      capture(fd, INFO, "ASSERT_EQ", subject, "receives " & to_str(received) & " and expects " & to_str(expected));
    else 
      capture(fd, ERROR, "ASSERT_EQ", subject, "receives " & to_str(received) & " but expects " & to_str(expected));
    end if;
  end procedure;

  procedure assert_ne(file fd: text; received: logic; expected: logic; subject: str) is
  begin
    if received /= expected then
      capture(fd, INFO, "ASSERT_NE", subject, "receives" & to_str(received) & " and does not expect " & to_str(expected));
    else 
      capture(fd, ERROR, "ASSERT_NE", subject, "receives " & to_str(received) & " but does not expect " & to_str(expected));
    end if;
  end procedure;

  procedure assert_ne(file fd: text; received: logics; expected: logics; subject: str) is
  begin
    if received /= expected then
      capture(fd, INFO, "ASSERT_NE", subject, "receives " & to_str(received) & " and expects anything except " & to_str(expected));
    else 
      capture(fd, ERROR, "ASSERT_NE", subject, "receives " & to_str(received) & " but expects anything except " & to_str(expected));
    end if;
  end procedure;

  procedure monitor(file fd: text; signal clk: logic; signal datum: logic; constant active: logic; constant cycles: usize; subject: str) is
    variable cycle_count: usize := 0;
    constant cycle_limit: usize := cycles + 1;
  begin
    -- wait forever if there is no clock cycle limit
    if cycle_limit = 0 then
      wait until falling_edge(clk) and datum = active;
      return;
    else
      -- wonky way to count cycles and evaluate on first edge of flag being asserted...
      -- maybe break monitor into 2 separate processes (a cycle counter and a rising flag detector)
      while cycle_count < cycle_limit loop
        if datum = active then
          capture(fd, INFO, "MONITOR", subject, "observes " & to_str(active) & " after waiting " & to_str(cycle_count) & " cycle(s)");
          return;
        end if;
        -- necessary ordering to escape at correct time in simulation
        cycle_count := cycle_count + 1;
        if cycle_count < cycle_limit then
          wait until falling_edge(clk);
        end if;
      end loop;
    end if;
    -- reached this point, then a violation has occurred
    capture(fd, ERROR, "MONITOR", subject, "fails to observe " & to_str(active) & " after waiting " & to_str(cycles) & " cycle(s)");
  end procedure;

  procedure monitor(file fd: text; signal clk: logic; signal data: logics; constant active: logics; constant cycles: usize; subject: str) is
    variable cycle_count: usize := 0;
    constant cycle_limit: usize := cycles + 1;
  begin
    -- wait forever if there is no clock cycle limit
    if cycle_limit = 0 then
      wait until falling_edge(clk) and data = active;
      return;
    else
      -- wonky way to count cycles and evaluate on first edge of flag being asserted...
      -- maybe break monitor into 2 separate processes (a cycle counter and a rising flag detector)
      while cycle_count < cycle_limit loop
        if data = active then
          capture(fd, INFO, "MONITOR", subject, "observes " & to_str(active) & " after waiting " & to_str(cycle_count) & " cycle(s)");
          return;
        end if;
        -- necessary ordering to escape at correct time in simulation
        cycle_count := cycle_count + 1;
        if cycle_count < cycle_limit then
          wait until falling_edge(clk);
        end if;
      end loop;
    end if;
    -- reached this point, then a violation has occurred
    capture(fd, ERROR, "MONITOR", subject, "fails to observe " & to_str(active) & " after waiting " & to_str(cycles) & " cycle(s)");
  end procedure;

  procedure stabilize(file fd: text; signal clk: logic; signal datum: logic; signal flag: logic; constant active: logic; subject: str) is
    variable prev_datum: logic;
    variable is_okay: bool := true;
    variable is_checked: bool := false;
    variable num_cycles: usize := 0;
  begin
    wait until rising_edge(clk);

    prev_datum := datum;
    while flag = active loop
      is_checked := true;
      -- check if its been stable since the rising edge of the flag
      if prev_datum /= datum then
        is_okay := false;
        capture(fd, ERROR, "STABILIZE", subject, "loses stability of " & to_str(prev_datum) & " by changing to " & to_str(datum) & " after " & to_str(num_cycles) & " cycle(s)");
      end if;

      wait until rising_edge(clk);
      num_cycles := num_cycles + 1;
    end loop;
    if is_checked = true and is_okay = true then
      capture(fd, INFO, "STABILIZE", subject, "keeps stability at " & to_str(prev_datum) & " for " & to_str(num_cycles) & " cycle(s)");
    end if;
  end procedure;

  procedure stabilize(file fd: text; signal clk: logic; signal data: logics; signal flag: logic; constant active: logic; subject: str) is
    variable prev_data: logics(data'range);
    variable is_okay: bool := true;
    variable is_checked: bool := false;
    variable num_cycles: usize := 0;
  begin
    wait until rising_edge(clk);

    prev_data := data;
    while flag = active loop
      is_checked := true;
      -- check if its been stable since the rising edge of done
      if prev_data /= data then
        is_okay := false;
        capture(fd, ERROR, "STABILIZE", subject, "loses stability of " & to_str(prev_data) & " by changing to " & to_str(data) & " after " & to_str(num_cycles) & " cycle(s)");
      end if;

      wait until rising_edge(clk);
      num_cycles := num_cycles + 1;
    end loop;
    if is_checked = true and is_okay = true then
      capture(fd, INFO, "STABILIZE", subject, "keeps stability at " & to_str(prev_data) & " for " & to_str(num_cycles) & " cycle(s)");
    end if;
  end procedure;
  

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
    variable word: str(x'range);
    variable temp: logics(x'range);
    variable delim: char;
  begin
    if row'length > 0 then
      read(row, word);
      for i in x'range loop
        temp(i) := to_logic(word(i));
      end loop;
      x <= temp;
      -- ignore the delimiter
      read(row, delim);
      -- wait for 0 ns;
    end if;
  end procedure;

  procedure load(variable row: inout line; variable x: out logics) is
    variable word: str(x'range);
    variable delim: char;
  begin
    if row'length > 0 then
      read(row, word);
      for i in x'range loop
        x(i) := to_logic(word(i));
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