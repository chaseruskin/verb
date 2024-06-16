-- Project: Vertex
-- Package: events
--
-- This package contains data recording procedures to capture events of 
-- interest during simulation.

library ieee;
use ieee.std_logic_1164.all;

library amp;
use amp.types.all;
use amp.cast.all;

library std;
use std.textio.all;

package events is

  -- Captures an event during simulation and writes the outcome to the file `fd`.
  -- The time when the procedure is called is recorded in the timestamp.
  procedure log_event(file fd: text; level: lvlog; topic: str; why: str; how: str := "");

  -- Asserts that two logic bits are equal to each other.
  procedure assert_eq(file fd: text; received: logic; expected: logic; details: str := "");

  -- Asserts that two logic vectors are equal to each other.
  procedure assert_eq(file fd: text; received: logics; expected: logics; details: str := "");

  -- Checks that the logic vector `vec` does not change value while `cond` is active (active-high).
  procedure stabilize_h(file fd: text; signal clk: logic; signal cond: logic; signal vec: logics; details: str := "");

  -- Checks that the logic vector `vec` does not change value while `cond` is active (active-low).
  procedure stabilize_l(file fd: text; signal clk: logic; signal cond: logic; signal vec: logics; details: str := "");

  -- Checks that the logic bit `flag` is activated (active-high) before timing out after `cycles` clock cycles.
  procedure monitor_h(file fd: text; signal clk: logic; signal flag: logic; cycles: usize; variable timeout: out bool; details: str := "");

  -- Checks that the logic bit `flag` is activated (active-low) before timing out after `cycles` clock cycles.
  procedure monitor_l(file fd: text; signal clk: logic; signal flag: logic; cycles: usize; variable timeout: out bool; details: str := "");

  -- The log level type.
  type lvlog is (TRACE, DEBUG, INFO, WARN, ERROR, FATAL);

end package;


package body events is

  procedure log_event(file fd: text; level: lvlog; topic: str; why: str; how: str := "") is
    variable row: line;
    variable topic_filtered: str(topic'range);
    constant TIMESTAMP_SHIFT: psize := 5 + 15;
    constant LOGLEVEL_SHIFT: psize := 8;
    constant TOPIC_SHIFT: psize := 12;

    function format_time(moment: str; size: psize) return str is
      variable padded: str(1 to size);
    begin
      if moment'length >= size then
        return moment;
      end if;
      for i in 1 to size - moment'length loop
        padded(i) := '0';
      end loop;
      padded(size - moment'length + 1 to padded'length) := moment;
      return padded;
    end function;

  begin

    -- write the timestamp ("when")
    write(row, '[');
    write(row, format_time(to_str(now), TIMESTAMP_SHIFT), left, TIMESTAMP_SHIFT);
    write(row, ']');

    -- write the log level ("why") ... TRACE, DEBUG, INFO, WARN, ERROR, FATAL
    write(row, ' ');
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

    -- write the topic ("what")
    write(row, ' ');
    -- filter the topic to prevent illegal characters from messing up format
    topic_filtered := topic;
    for ii in topic'range loop
        if topic(ii) = '"' then
            topic_filtered(ii) := '_';
            assert false report "LOG.LOG_EVENT: converting '""' to '_' in event name" severity warning;
        elsif topic(ii) = ' ' then
            topic_filtered(ii) := '_';
            assert false report "LOG.LOG_EVENT: converting ' ' to '_' in event name" severity warning;
        end if;
    end loop;
    write(row, topic_filtered, left, TOPIC_SHIFT);

    -- write the high-level summary of why this event was triggered
    write(row, ' ');
    write(row, '"');
    write(row, why);
    write(row, '"');

    -- write additional details pertaining to how this event happened
    if how /= "" then
      write(row, ' ');
      write(row, '"');
      write(row, how);
      write(row, '"');
    end if;

    writeline(fd, row);
  end procedure;


  procedure assert_eq(file fd: text; received: logic; expected: logic; details: str := "") is
  begin
    if received = expected then
      log_event(fd, INFO, "ASSERT_EQ", to_str(received) & " (received) is equal to " & to_str(expected) & " (expected)", details);
    else 
      log_event(fd, ERROR, "ASSERT_EQ", to_str(received) & " (received) is not equal to " & to_str(expected) & " (expected)", details);
    end if;
  end procedure;


  procedure assert_eq(file fd: text; received: logics; expected: logics; details: str := "") is
  begin
    if received = expected then
      log_event(fd, INFO, "ASSERT_EQ", to_str(received) & " (received) is equal to " & to_str(expected) & " (expected)", details);
    else
      log_event(fd, ERROR, "ASSERT_EQ", to_str(received) & " (received) is not equal to " & to_str(expected) & " (expected)", details);
    end if;
  end procedure;


  procedure monitor_h(file fd: text; signal clk: logic; signal flag: logic; cycles: usize; variable timeout: out bool; details: str := "") is
    variable cycle_count: usize := 0;
    constant cycle_limit: usize := cycles + 1;
  begin
    timeout := true;
    -- wait forever if there is no clock cycle limit
    if cycle_limit = 0 then
      wait until falling_edge(clk) and flag = '1';
      timeout := false;
      return;
    else
      -- wonky way to count cycles and evaluate on first edge of flag being asserted...
      -- maybe break monitor into 2 separate processes (a cycle counter and a rising flag detector)
      while cycle_count < cycle_limit loop
        if flag = '1' then
          timeout := false;
          log_event(fd, INFO, "MONITOR_H", "Active after waiting " & to_str(cycle_count) & " cycles", details);
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
    log_event(fd, ERROR, "MONITOR_H", "Failed to activate after waiting " & to_str(cycles) & " cycles", details);
  end procedure;


  procedure monitor_l(file fd: text; signal clk: logic; signal flag: logic; cycles: usize; variable timeout: out bool; details: str := "") is
    variable cycle_count: usize := 0;
    constant cycle_limit: usize := cycles + 1;
  begin
    timeout := true;
    -- wait forever if there is no clock cycle limit
    if cycle_limit = 0 then
      wait until falling_edge(clk) and flag = '0';
      timeout := false;
      return;
    else
      -- wonky way to count cycles and evaluate on first edge of flag being asserted...
      -- maybe break monitor into 2 separate processes (a cycle counter and a rising flag detector)
      while cycle_count < cycle_limit loop
        if flag = '0' then
          timeout := false;
          log_event(fd, INFO, "MONITOR_L", "Active after waiting " & to_str(cycle_count) & " cycles", details);
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
    log_event(fd, ERROR, "MONITOR_L", "Failed to activate after waiting " & to_str(cycles) & " cycles", details);
  end procedure;

  
  procedure stabilize_h(file fd: text; signal clk: logic; signal cond: logic; signal vec: logics; details: str := "") is
    variable vec_prev: logics(vec'range);
    variable is_okay: bool := true;
  begin
    wait until rising_edge(cond);
    -- wait until rising_edge(cond);
    vec_prev := vec;
    while cond = '1' loop
      -- check if its been stable since the rising edge of done
      if vec_prev /= vec then
        is_okay := false;
        log_event(fd, ERROR, "STABILIZE_H", "Lost stability of " & to_str(vec_prev) & " by changing to " & to_str(vec), details);
      end if;

      wait until rising_edge(clk);
    end loop;
    if is_okay = true then
      log_event(fd, INFO, "STABILIZE_H", "Kept stability at " & to_str(vec_prev), details);
    end if;
  end procedure;


  procedure stabilize_l(file fd: text; signal clk: logic; signal cond: logic; signal vec: logics; details: str := "") is
    variable vec_prev: logics(vec'range);
    variable is_okay: bool := true;
  begin
    wait until rising_edge(cond);
    -- wait until rising_edge(cond);
    vec_prev := vec;
    while cond = '0' loop
      -- check if its been stable since the rising edge of done
      if vec_prev /= vec then
        is_okay := false;
        log_event(fd, ERROR, "STABILIZE_L", "Lost stability of " & to_str(vec_prev) & " by changing to " & to_str(vec), details);
      end if;

      wait until rising_edge(clk);
    end loop;
    if is_okay = true then
      log_event(fd, INFO, "STABILIZE_L", "Kept stability at " & to_str(vec_prev), details);
    end if;
  end procedure;

end package body;