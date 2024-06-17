library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library amp;
use amp.prelude.all;

entity add is
    generic (
        WORD_SIZE: psize
    );
    port (
        cin: in logic;
        in0: in logics(WORD_SIZE-1 downto 0);
        in1: in logics(WORD_SIZE-1 downto 0);
        sum: out logics(WORD_SIZE-1 downto 0);
        cout: out logic
    );
end entity;

architecture gp of add is
    signal result: logics(WORD_SIZE-1+1 downto 0);

    signal cins: logics(WORD_SIZE-1 downto 0) := (others => '0');
    signal temp: logics(WORD_SIZE-1+1 downto 0);

begin
    cins(0) <= cin;

    temp <= logics(usign('0' & in0) + usign('0' & in1));
    result <= logics(usign(temp) + usign(cins));

    cout <= result(WORD_SIZE);
    sum <= result(WORD_SIZE-1 downto 0);

end architecture;