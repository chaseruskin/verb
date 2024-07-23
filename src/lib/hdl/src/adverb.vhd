-- Project: Verb
-- Package: adverb
--
-- Functions available only for internal use with other Verb packages.

library ieee;
use ieee.std_logic_1164.all;

package adverb is

  -- An unresolved logic type.
  subtype logic is std_ulogic;

  -- A fixed-size array of `logic` element types.
  subtype logics is std_ulogic_vector;

  -- A resolved logic type.
  subtype rlogic is std_logic;

  -- A fixed-size array of `rlogic` element types.
  subtype rlogics is std_logic_vector;

  -- The compiler-sized signed integer type.
  subtype isize is integer;

  -- The compiler-sized unsigned integer type.
  subtype usize is natural;

  -- The compiler-sized positive integer type.
  subtype psize is positive;

  -- The compiler-sized signed integer type.
  subtype int is integer;

  -- The compiler-sized unsigned integer type.
  subtype uint is natural;

  -- The compiler-sized positive integer type.
  subtype pint is positive;

  -- The boolean type.
  subtype bool is boolean;  
  
  -- A character type.
  subtype char is character;

  -- A fixed-size array of `char` element types.
  subtype str is string;

  -- A fixed-size array of `bit` element types.
  subtype bits is bit_vector;

  -- Casts a logic vector to a string.
  function to_str(v: logics) return str;

  -- Casts a logic bit to a string.
  function to_str(b: logic) return str;

  -- Casts an integer to a string.
  function to_str(k: int) return str;

  -- Casts a boolean to a string.
  function to_str(b: bool) return str;

  -- Casts a time to a string.
  function to_str(t: time) return str;

  -- Casts a real to a string.
  function to_str(r: real) return str;

  -- Casts a character to a logic bit.
  function to_logic(c: char) return logic;

  -- Casts a logic bit to a logic vector.
  function to_logics(b: logic) return logics;

end package;


package body adverb is

  function to_str(v: logics) return str is
    variable word: str(1 to v'length);
    variable idx_word: psize := 1;
    variable b: logic;
  begin
    for idx in v'range loop
      b := v(idx);
      if b = '1' then
        word(idx_word) := '1';
      elsif b = '0' then
        word(idx_word) := '0';
      elsif b = 'X' then
        word(idx_word) := 'X';
      elsif b = 'U' then
        word(idx_word) := 'U';
      elsif b = 'Z' then
        word(idx_word) := 'Z';
      elsif b = 'W' then
        word(idx_word) := 'W';
      elsif b = 'L' then
        word(idx_word) := 'L';
      elsif b = 'H' then
        word(idx_word) := 'H';
      elsif b = '-' then
        word(idx_word) := '-';
      else
        assert false report "ADVERB.TO_STR: unsupported logic value" severity warning;
        word(idx_word) := '?';
      end if;
      idx_word := idx_word + 1;
    end loop;
    return word;
  end function;


  function to_str(b: logic) return str is
    variable word: str(1 to 1);
  begin
    if b = '1' then
      word(1) := '1';
    elsif b = '0' then
      word(1) := '0';
    elsif b = 'X' then
      word(1) := 'X';
    elsif b = 'U' then
      word(1) := 'U';
    elsif b = 'Z' then
      word(1) := 'Z';
    elsif b = 'W' then
      word(1) := 'W';
    elsif b = 'L' then
      word(1) := 'L';
    elsif b = 'H' then
      word(1) := 'H';
    elsif b = '-' then
      word(1) := '-';
    else
      assert false report "ADVERB.TO_STR: unsupported logic value" severity warning;
      word(1) := '?';
    end if;
    return word;
  end function;


  function to_str(k: int) return str is
  begin
    return int'image(k);
  end function;


  function to_str(b: bool) return str is
  begin
    return bool'image(b);
  end function;


  function to_str(t: time) return str is
  begin
    return time'image(t);
  end function;


  function to_str(r: real) return str is
  begin
    return real'image(r);
  end function;


  function to_logic(c: char) return logic is
  begin
    if c = '1' then
      return '1';
    elsif c = '0' then
      return '0';
    elsif c = 'X' then
      return 'X';
    elsif c = 'U' then
      return 'U';
    elsif c = 'Z' then
      return 'Z';
    elsif c = 'W' then
      return 'W';
    elsif c = 'L' then
      return 'L';
    elsif c = 'H' then
      return 'H';
    elsif c = '-' then
      return '-';
    else
      assert false report "ADVERB.TO_LOGIC: unsupported character" severity warning;
      return '0';
    end if;
  end function;

  
  function to_logics(b: logic) return logics is
    variable v: logics(0 downto 0);
  begin
    v(0) := b;
    return v;
  end function;

end package body;