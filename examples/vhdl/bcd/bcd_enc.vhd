--------------------------------------------------------------------------------
--! Project  : eel4712c.lab5
--! Engineer : Chase Ruskin
--! Course   : Digital Design - EEL4712C
--! Created  : 2021-10-16
--! Entity   : bcd_enc
--! Details  :
--!     Encodes a binary number `bin` into a binary-coded decimal number `bcd` 
--!     using the "double dabble" algorithm. 
--!     
--!     Implemented with a 2-process FSMD. If at any point during the  
--!     computation the input number changes, the algorithm resets. On the same
--!     cycle that done is asserted, the output is ready on `bcd` and `ovfl`.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library nano;
use nano.amp.all;
use nano.math.all;
use nano.dims.all;

entity bcd_enc is
    generic (
        --! width of incoming binary number
        LEN : positive range 2 to positive'high := 4; 
        --! number of decimal digits to use
        DIGITS : positive := 2 
    );
    port (
        rst   : in  logic;  
        clk   : in  logic;
        --! enable flag (starts the algorithm)
        go    : in  logic;  
        bin   : in  logics(LEN-1 downto 0);
        bcd   : out logics((4*DIGITS)-1 downto 0);
        done  : out logic;
        --! flag to indicate if not enough digits were specified
        ovfl  : out logic   
    );
end entity;


architecture gp of bcd_enc is

    type state is (S_LOAD, S_SHIFT, S_ADD, S_COMPLETE, S_WAIT);

    -- register and next-cycle wire for dabble
    signal dabble_r : logics(bcd'length+bin'length-1 downto 0);
    signal dabble_d : logics(bcd'length+bin'length-1 downto 0);

    -- register and next-cycle wire for overflow
    signal ovfl_r : logic;
    signal ovfl_d : logic;

    -- register and next-cycle wire for state
    signal state_r : state;
    signal state_d : state;

    -- register to store the current binary representation being processed
    signal bin_r : logics(LEN-1 downto 0);

    -- amount of bits needed is how many are to be used to represent binary input's bit width
    constant CTR_LEN : positive := clog2(LEN);

    -- register and next-cycle wire for counter
    signal ctr_r : logics(CTR_LEN-1 downto 0);
    signal ctr_d : logics(CTR_LEN-1 downto 0);

begin
    -- simple pass-through
    ovfl <= ovfl_r;

    --! combinational logic to determine next state and output signals
    process(state_r, ctr_r, dabble_r, ovfl_r, go, bin)
        variable v_bcd_digit : logics(3 downto 0);
        variable v_dabble_d  : logics(dabble_d'range);
    begin
        -- defaults
        state_d <= state_r;
        ctr_d <= ctr_r;
        ovfl_d <= ovfl_r;
        dabble_d <= dabble_r;
        done <= '0';
        bcd <= dabble_r(dabble_r'length-1 downto LEN);

        case state_r is
            --! collect data for algorithm computation
            when S_LOAD => 
                -- load in binary number
                dabble_d <= (others => '0');
                dabble_d(bin'length-1 downto 0) <= bin;
                -- reset the counter
                ctr_d <= (others => '0');
                ovfl_d <= '0';

                -- transition to begin the algorithm
                if go = '1' then
                    state_d <= S_SHIFT;
                end if;
            
            --! perform "double" (multiply by 2)
            when S_SHIFT =>
                -- perform left S_SHIFT
                dabble_d <= shift_left_logic(dabble_r, 1);
                -- trip when the bit getting pushed off is a '1'
                ovfl_d <= ovfl_r or dabble_r(dabble_r'length-1);
                -- increment the counter
                ctr_d <= logics(usign(ctr_r) + to_usign(1, ctr_r'length));
                -- algorithm is done when the current count reaches MAX_CTR
                if ctr_r = logics(to_usign(LEN-1, ctr_r'length)) then
                    state_d <= S_COMPLETE;
                -- otherwise continue the algorithm
                else
                    state_d <= S_ADD;
                end if;
            
            --! perform "dabble" (+3 when >=5)
            when S_ADD =>
                v_dabble_d := dabble_r;
                -- evaluate every BCD digit at this stage
                for ii in DIGITS-1 downto 0 loop
                    -- v_bcd_digit := dabble_r((4*(ii+1))+LEN-1 downto (4*ii)+LEN);
                    v_bcd_digit := get_slice(dabble_r, v_bcd_digit, ii, LEN);
                    -- add 3 to bcd digit when the value is greater than or equal to 5
                    if v_bcd_digit >= logics(to_usign(5, v_bcd_digit'length)) then
                        -- dabble_d((4*(ii+1))+LEN-1 downto (4*ii)+LEN) <= logics(unsigned(tmp_bcd_digit) + 3);
                        -- v_dabble_d(index_2d1d(ii, v_bcd_digit'length, LEN)'range) := v_bcd_digit + 3;
                        v_dabble_d := set_slice(v_dabble_d, logics(usign(v_bcd_digit) + to_usign(3, v_bcd_digit'length)), ii, LEN);
                    end if;
                end loop;
                dabble_d <= v_dabble_d;
                -- transition back to S_SHIFT
                state_d <= S_SHIFT;

            --! algorithm complete; output results
            when S_COMPLETE =>
                -- signify that the output data is valid
                done <= '1';
                -- output overflow flag
                ovfl_d <= ovfl_r;
                -- transition back to the beginning state
                state_d <= S_WAIT;
            
            when S_WAIT =>
                done <= '1';
                -- uncomment this line to see stability errors
                -- bcd <= (others => '0');
                state_d <= S_LOAD;

            --! default case
            when others =>
                null;
        end case;

    end process;
    
    --! sequential logic for storing FSM registers
    process(rst, clk)
    begin
        if rst = '1' then
            ovfl_r <= '0';
            dabble_r <= (others => '0');
            bin_r <= (others => '0');
            ctr_r <= (others => '0');
            state_r <= S_LOAD;
        elsif rising_edge(clk) then
            state_r <= state_d;
            ctr_r <= ctr_d;
            ovfl_r <= ovfl_d;
            dabble_r <= dabble_d;
            bin_r <= bin;
        end if;
    end process;

end architecture;