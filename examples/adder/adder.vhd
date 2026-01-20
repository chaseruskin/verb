library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder is
    generic (
        WORD_SIZE: positive
    );
    port (
        cin: in std_ulogic;
        in0: in std_ulogic_vector(WORD_SIZE-1 downto 0);
        in1: in std_ulogic_vector(WORD_SIZE-1 downto 0);
        sum: out std_ulogic_vector(WORD_SIZE-1 downto 0);
        cout: out std_ulogic
    );
end entity;


architecture rtl of adder is

    signal result: std_ulogic_vector(WORD_SIZE-1+1 downto 0);

    signal cins: std_ulogic_vector(WORD_SIZE-1 downto 0) := (others => '0');
    signal temp: std_ulogic_vector(WORD_SIZE-1+1 downto 0);

begin

    cins(0) <= cin;

    temp <= std_ulogic_vector(unsigned('0' & in0) + unsigned('0' & in1));
    result <= std_ulogic_vector(unsigned(temp) + unsigned(cins));

    cout <= result(WORD_SIZE);
    sum <= result(WORD_SIZE-1 downto 0);

end architecture;
