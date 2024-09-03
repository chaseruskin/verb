library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library amp;
use amp.prelude.all;
use amp.math.all;

entity timer is
  generic (
    -- Common delay among all sub-counters for cycles
    BASE_DELAY: psize;
    -- Counters that increment off the base count overflowing. This value 
    -- effectively gets "multiplied" to the 'BASE_DELAY'.
    SUB_DELAYS: psizes
  );
  port (
    rst: in  logic;
    clk: in  logic;
    base_tick: out logic;
    sub_ticks: out logics(SUB_DELAYS'left to SUB_DELAYS'right)
  );
end entity;

architecture gp of timer is

  function maximum(arr: psizes) return psize is
    variable max: int := arr'left;
  begin
    for i in arr'left to arr'right loop
      if arr(i) > max then
        max := arr(i);
      end if;
    end loop;   
    return max;
  end function;

  type logics2d is array (usize range SUB_DELAYS'left to SUB_DELAYS'right) of logics(clog2(maximum(SUB_DELAYS))-1 downto 0);

  signal sub_counts: logics2d;

  -- must be able to wait 'BASE_DELAY' number of cycles
  signal base_count: logics(clog2(BASE_DELAY)-1 downto 0);

begin

  tick: process(rst, clk) is
    variable base_tick_v: logic;
  begin
    if rst = '1' then
      -- reset counters
      for i in sub_counts'range loop
        sub_counts(i) <= (others => '0');
      end loop;
      
      -- reset base counter
      base_count <= (others => '0');

      sub_ticks <= (others => '0');
      base_tick <= '0';

    elsif rising_edge(clk) then
      base_tick_v := '0';

      -- increment the counter
      base_count <= logics(usign(base_count) + to_usign(1, base_count'length));
      -- check if we have counted 'BASE_DELAY' clock cycles
      if base_count = logics(to_usign(BASE_DELAY-1, base_count'length)) then
          base_tick_v := '1';
          base_count <= (others => '0');
      end if;

      -- always start from cleared state
      sub_ticks <= (others => '0');

      -- only increment when the base counter has reached its limit
      if base_tick_v = '1' then
        -- visit every sub-counter
        for i in sub_counts'range loop
          -- increment the sub-counter
          sub_counts(i) <= logics(usign(sub_counts(i)) + to_usign(1, sub_counts(i)'length));
          -- check if the tick should overflow
          if sub_counts(i) = logics(to_usign(SUB_DELAYS(i)-1, sub_counts(i)'length)) then
            sub_ticks(i) <= '1';
            sub_counts(i) <= (others => '0');
          end if;
        end loop;
      end if;

      -- update signals at the end of process
      base_tick <= base_tick_v;
    end if;
  end process;

end architecture;