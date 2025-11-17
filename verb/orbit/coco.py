import os
import sys
import json

import cocotb_tools.config as cocotb_config
from aquila import env
from aquila.blueprint import Blueprint, Entry
from aquila.env import Seed

class Cocotb:
    """
    An abstraction layer for invoking cocotb simulations.
    """

    def __init__(self, cocotb_fset: str, seed: Seed, time_res: str):
        """
        Initializes are necessary environment variables for cocotb.
        """
        # try to find the test module
        entries = Blueprint().get_entries()
        # determine what the top level language is
        entry: Entry
        self.toplevel_lang = None
        self.rand_seed = seed
        self.cocotb_test_modules = []
        self.cocotb_hdl_timeprec = time_res
        python_module_dirs = []
        for entry in entries:
            if entry.fset == 'VHDL':
                self.toplevel_lang = 'vhdl'
            elif entry.fset == 'SYSV' or entry.fset == 'VLOG':
                self.toplevel_lang = 'verilog'
            if entry.fset == cocotb_fset:
                self.cocotb_test_modules += [os.path.splitext(os.path.basename(entry.path))[0]]
                python_module_dirs += [os.path.dirname(entry.path)]

        # try to determine the toplevel
        dut_name = env.read('ORBIT_DUT_NAME')
        tb_name = env.read('ORBIT_TB_NAME')
        
        self.cocotb_toplevel = dut_name if tb_name is None else tb_name

        for mod_dir in python_module_dirs:
            env.prepend('PYTHONPATH', mod_dir)
            print(env.read('PYTHONPATH'))

        env.write('TOPLEVEL_LANG', self.toplevel_lang)
        env.write('COCOTB_TOPLEVEL', self.cocotb_toplevel)
        env.write('COCOTB_TEST_MODULES', ','.join(self.cocotb_test_modules))
        env.write('COCOTB_REDUCED_LOG_FMT', '1')

        ansi_output = '1' if env.read('NO_COLOR') is None else '0'
        
        env.write('COCOTB_ANSI_OUTPUT', ansi_output)
        env.write('COCOTB_HDL_TIMEPRECISION', self.cocotb_hdl_timeprec)

        env.write('PYGPI_PYTHON_BIN', self.get_pygpi_python_bin())
        env.write('LIBPYTHON_LOC', self.get_lib_python_loc())
        env.write('COCOTB_RANDOM_SEED', str(self.rand_seed.get_seed()))

    def get_test_mod(self) -> str:
        """
        Returns the COCOTB test module, if one was found. Otherwise, returns None.
        """
        if len(self.cocotb_test_modules) == 0:
            return None
        return ','.join(self.cocotb_test_modules)

    def get_lib_name_path(self, interface: str, simulator: str) -> str:
        return str(cocotb_config.lib_name_path(interface, simulator))
    
    def get_pygpi_python_bin(self) -> str:
        return str(sys.executable)
    
    def get_lib_python_loc(self) -> str:
        """
        Returns the path to the Python shared library file.
        """
        if env.read('LIBPYTHON_LOC') is not None:
            return env.read('LIBPYTHON_LOC')
        import find_libpython
        libpython_path = find_libpython.find_libpython()
        if libpython_path is None:
            print('error: missing value for environment variable LIBPYTHON_LOC')
            exit(101)
        return str(libpython_path)
    
    def is_missing_tb(self) -> bool:
        """
        Returns true if a testbench was not listed in the sources.

        This most likely indicates that the target scripts are responsible for
        creating a testbench wrapper.
        """
        return env.read('ORBIT_TB_NAME') is None
    
    def generate_tb(self, dut_name: str, dut_path: str) -> str:
        """
        Generates a VHDL testbench file for the dut, if one does not exist.

        Returns the path to the generated testbench file, or None if one already exists.
        """
        if self.is_missing_tb() == False:
            return None
        tb_name = dut_name + '_tb'
        tb_path = env.read('ORBIT_OUT_DIR') + '/' + tb_name + '.vhd'

        # check if tb data already exists
        prev_tb_data = ''
        if os.path.exists(tb_path) == True:
            with open(tb_path, 'r') as fd:
                prev_tb_data = fd.read()
        
        # get the structured data about the dut
        dut_json = json.loads(env.read('ORBIT_DUT_JSON'))

        dut_generics = dut_json['generics']
        dut_signals = dut_json['ports']

        dut_clk = None
        for signal in dut_signals:
            s_name = signal['identifier']
            if signal['mode'].lower() != 'in':
                continue
            if s_name.lower().startswith('clk') or s_name.lower().endswith('clk'):
                dut_clk = signal
                break

        tb_data = ''
        dut_data = ''
        with open(dut_path, 'r') as fd:
            dut_data = fd.read()

        # collect the dut's import/include statements
        includes = []
        dut_lines = dut_data.splitlines()
        for line in dut_lines:
            line = line.strip()
            if line.lower().startswith('--') or len(line) == 0:
                continue
            if line.lower().startswith('entity '+dut_name.lower()):
                break
            includes += [line]

        tb_data = '-- This file is automatically @generated by Orbit.\n-- It is not intended for manual editing.\n'
        tb_data += '\n'.join(includes)

        if len(includes) > 0:
            tb_data += '\n'

        tb_data += '\nentity '+tb_name+' is'

        if len(dut_generics) > 0:
            tb_data += '\n  generic ('
            for (i, g) in enumerate(dut_generics):
                tb_data += '\n    '+g['identifier'] + ': '+g['mode']+' '+g['type']
                if g['default'] is not None:
                    tb_data += ' := '+g['default']
                if i+1 < len(dut_generics):
                    tb_data += ';'
            tb_data += '\n  );'
        
        tb_data += '\nend entity;'
        
        # write the architecture declaration section
        tb_data += '\n\narchitecture tst of '+tb_name+' is'
        
        if len(dut_signals) > 0:
            tb_data += '\n'
            for s in dut_signals:
                tb_data += '\n  signal '+s['identifier']+': '+s['type']
                # check if this is the clock and assign default if so
                is_clk = dut_clk is not None and s['identifier'] == dut_clk['identifier']
                if s['default'] is not None and not is_clk:
                    tb_data += ' := '+g['default']
                elif is_clk:
                    tb_data += ' := \'0\''
                tb_data += ';'
            tb_data += '\n'

        # add in clock if missing
        if dut_clk is None:
            tb_data += '\n  signal clk : bit := \'0\';\n'

        # write the architecture body
        tb_data += '\nbegin\n'

        # add in clock process
        # clk_name = 'clk' if dut_clk is None else dut_clk['identifier']

        # tb_data += '\n  spinner: process\n  begin\n    '+clk_name +' <= \'0\';'
        # tb_data += '\n    while true loop'
        # tb_data += '\n      wait for 10 ns;'
        # tb_data += '\n      '+clk_name+' <= not '+clk_name+';'
        # tb_data += '\n    end loop;'
        # tb_data += '\n    wait;'
        # tb_data += '\n  end process;\n'

        # use continuous assignment so we can freeze/release the signal so GHDL can gracefully terminate
        # tb_data += '\n  '+clk_name+' <= not '+clk_name+' after 10 ns;\n'

        # instantiate the design under test
        tb_data += '\n  dut : entity work.'+dut_name+'\n '
        if len(dut_generics) > 0:
            tb_data += ' generic map ('
            for (i, g) in enumerate(dut_generics):
                tb_data += '\n    '+g['identifier']+' => '+g['identifier']
                if i+1 < len(dut_generics):
                    tb_data += ','
            tb_data += '\n  )'
        if len(dut_signals) > 0:
            tb_data += ' port map ('
            for (i, p) in enumerate(dut_signals):
                tb_data += '\n    '+p['identifier']+' => '+p['identifier']
                if i+1 < len(dut_signals):
                    tb_data += ','
            tb_data += '\n  )'
        tb_data += ';\n'

        tb_data += '\nend architecture;\n'
        
        # write the testbench contents to a file only if needs to be updated
        if tb_data != prev_tb_data:
            with open(tb_path, 'w') as fd:
                fd.write(tb_data)

        # update the toplevel for cocotb
        env.write('COCOTB_TOPLEVEL', tb_name)
        return tb_path
