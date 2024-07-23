library ieee;
use ieee.std_logic_1164.all;

library std;
use std.textio.all;

library amp;
use amp.prelude.all;

library test;
use test.verb.all;

entity timer_tb is
  generic(
    BASE_DELAY: psize := 4;
    SUB_DELAYS: psizes := (2, 4, 10, 19, 32)
  );
end entity;


architecture sim of timer_tb is

  type timer_bfm is record
    base_tick: logic;
    sub_ticks: logics(SUB_DELAYS'left to SUB_DELAYS'right);
  end record;
  
  signal bfm: timer_bfm;

  signal clk: logic := '0';
  signal rst: logic := '0';
  signal halt: bool := false;

  -- Declare internal required testbench signals
  constant TIMEOUT_LIMIT: usize := 1_000;

  file events: text open write_mode is "events.log";

begin

  -- instantiate dut
  dut: entity work.timer
    generic map (
      BASE_DELAY => BASE_DELAY,
      SUB_DELAYS => SUB_DELAYS
    ) 
    port map (
      rst => rst,
      clk => clk,
      base_tick => bfm.base_tick,
      sub_ticks => bfm.sub_ticks
    );

  -- generate a 50% duty cycle for 25 MHz
  spin_clock(clk, 40 ns, halt);

  -- test reading a file filled with test vectors
  produce: process
      file inputs: text open read_mode is "inputs.txt";

      procedure send(file i: text) is 
        variable row: line;
      begin
        if endfile(i) = false then
          readline(i, row);
        end if;
      end procedure;

  begin  
    -- power-on reset
    trigger_async(clk, rst, '1', 2);

    -- drive transactions
    while endfile(inputs) = false loop
      send(inputs);
      wait until rising_edge(clk);
    end loop;

    -- wait for all outputs to be checked
    wait;
  end process;

  consume: process
    file outputs: text open read_mode is "outputs.txt";

    procedure compare(file e: text; file o: text) is
      variable row: line;
      variable expct: timer_bfm;
    begin
      if endfile(o) = false then
        readline(o, row);
        load(row, expct.base_tick);
        assert_eq(e, bfm.base_tick, expct.base_tick, "base_tick");
        load(row, expct.sub_ticks);
        assert_eq(e, bfm.sub_ticks, expct.sub_ticks, "sub_ticks");
      end if;
    end procedure;

  begin
    wait until falling_edge(rst);
    wait until rising_edge(clk);

    while endfile(outputs) = false loop
      -- wait for a valid time to check
      wait until rising_edge(clk);
      -- compare outputs
      compare(events, outputs);
    end loop;

    -- halt the simulation
    complete(halt);
  end process;

end architecture;