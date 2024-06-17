library ieee;
use ieee.std_logic_1164.all;

library amp;
use amp.types.all;

entity basic is 
    port(
        rx  : in logic;
        tx  : out logic;
        valid : out logic
    );
end entity;

architecture gp of basic is
begin

    tx <= not rx;
    valid <= '1';

end architecture;

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

library work;
use work.events.all;
use work.tutils.all;

library amp;
use amp.types.all;

entity basic_tb is
end entity;

architecture sim of basic_tb is

    constant WIDTH_A : positive := 12;

    --! internal test signals
    signal slv0 : logics(WIDTH_A-1 downto 0) := (others => '0');
    signal slv1 : logics(WIDTH_A-1 downto 0) := (others => '0');
    signal slv2 : logics(7 downto 0) := (others => '0');
    signal sl0 : logic;

    signal rx : logic := '0';
    signal tx : logic := '0';
    signal valid : logic := '0';

    constant TIMEOUT_LIMIT : natural := 1000;

    -- always include these signals in a testbench
    signal clk   : logic;
    signal reset : logic := '0';
    signal halt  : boolean := false;

    file events : text open write_mode is "events.log";

begin
    -- unit-under-test
    dut: entity work.basic 
        port map(
            tx => tx,
            rx => rx,
            valid => valid
        );

    --! Generate a 50% duty cycle for 25 Mhz
    spin_clock(clk, 40 ns, halt);

    --! test reading a file filled with test vectors
    producer: process
        file inputs : text open read_mode is "inputs.txt";

        -- @note: auto-generate procedure from python script because that is where
        -- order is defined for test vector inputs
        procedure send(file fd: text) is 
            variable row : line;
        begin
            if endfile(fd) = false then
                -- drive a transaction
                readline(fd, row);
                drive(row, slv0);
                drive(row, slv1);
                drive(row, sl0);
                drive(row, rx);
            end if;
        end procedure;

    begin  
        -- initialize input signals      
        send(inputs);
        trigger_async(clk, reset, '1', 4);
        wait until rising_edge(clk);

        -- drive transactions
        while endfile(inputs) = false loop
            send(inputs);
            wait until rising_edge(clk);
        end loop;

        -- wait for all outputs to be checked
        wait;
    end process;

    consumer: process
        file outputs : text open read_mode is "outputs.txt";
        variable timeout : boolean;

        -- @note: auto-generate procedure from python script because that is where
        -- order is defined for test vector outputs
        procedure compare(file fd: text) is
            variable row: line;
            variable ideal_tx: logic;
        begin
            if endfile(fd) = false then
                -- compare expected outputs and inputs
                readline(fd, row);
                load(row, ideal_tx);
                assert_eq(events, tx, ideal_tx, "tx");
            end if;
        end procedure;

    begin
        monitor(events, clk, reset, '1', 1000, "reset");
        monitor(events, clk, reset, '0', 1000, "reset");

        while endfile(outputs) = false loop
            -- wait for a valid time to check
            monitor(events, clk, valid, '1', TIMEOUT_LIMIT, "valid");
            -- compare outputs
            compare(outputs);
            wait until rising_edge(clk);
        end loop;

        -- use a custom log record (demonstrates filtering of topic too)
        if valid = '1' then
            capture(events, TRACE, "MEM_ACCESS", "cache", "hit");
        else 
            capture(events, TRACE, "MEM_ACCESS", "cache", "miss");
        end if;
        
        -- force an ERROR assertion into log
        assert_eq(events, valid, '1', "valid");
        assert_ne(events, tx, '1', "txt");

        -- halt the simulation
        complete(halt);
    end process;

end architecture;