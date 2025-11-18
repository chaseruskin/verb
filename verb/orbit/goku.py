'''
Backend target process for simulations with GHDL + cocotb + verb.
'''

import argparse
import sys

from aquila import log
from aquila import env
from aquila.blueprint import Entry
from aquila.env import KvPair, Seed
from aquila.ghdl import Ghdl, Mode
from aquila.cocoa import Cocotb, LogLvl

from verb.orbit.adverb import Verb

class Goku:
    '''
    Simulation workflow for GHDL + cocotb + verb.
    '''

    def __init__(self, ghdl: Ghdl, cocotb: Cocotb, verb: Verb):
        '''
        Construct a new Goku instance.
        '''
        self.ghdl = ghdl
        self.cocotb = cocotb
        self.verb = verb
        # attempt to generate a testbench if one is missing
        auto_tb_path = self.cocotb.generate_tb(ghdl.top_sim_name, ghdl.dut_path)
        if auto_tb_path is not None:
            ghdl.top_sim_name += '_tb'
            ghdl.tb_name = ghdl.top_sim_name
            ghdl.entries += [Entry('VHDL', ghdl.top_sim_lib, auto_tb_path, [ghdl.entries[-1].path])]

    @staticmethod
    def from_args(args: list):
        '''
        Construct a new Goku instance from a set of arguments.
        '''
        parser = argparse.ArgumentParser('goku', allow_abbrev=False)

        parser.add_argument('--run', '-r', action='store', choices=Mode.choices(), default=Mode.SIM, help='the mode to run')
        parser.add_argument('--log', metavar='LEVEL', choices=LogLvl.choices(), default=LogLvl.INFO, help='set the messaging log level')
        parser.add_argument('--generic', '-g', action='append', type=KvPair.from_arg, default=[], metavar='KEY=VALUE', help='set top-level generics')
        parser.add_argument('--filter', '-f', action='append', default=[], type=str, help='set specific test names to run')
        parser.add_argument('--seed', metavar='NUM', action='store', default=Seed(), type=Seed.from_str, help='set random seed')
        parser.add_argument('--timescale', '-t', metavar='UNIT', default='ps', help='set the simulation time resolution')

        args = parser.parse_args(args)
        ghdl = Ghdl(
            mode=Mode.from_arg(args.run),
            generics=args.generic,
            seed=args.seed,
            time_res=args.timescale,
        )
        cocotb = Cocotb(
            fileset='COCOTB-PY',
            seed=ghdl._seed,
            time_res='1'+ghdl._time_res,
            log_lvl=LogLvl.from_arg(args.log),
            test_filter=args.filter,
        )
        verb = Verb(
            generics=ghdl._generics
        )
        return Goku(
            ghdl=ghdl,
            cocotb=cocotb,
            verb=verb
        )
    
    def prepare(self):
        env.verify_all_generics_have_values(env.read('ORBIT_DUT_JSON'), self.ghdl._generics)
        if self.cocotb.get_test_mod() is None and self.ghdl._mode != 'com':
            log.error('cocotb test requires a python module to test')
        self.ghdl.prepare()

    def compile(self):
        self.ghdl.compile()

    def run(self):
        extra_args = ['--vpi='+self.cocotb.get_lib_name_path('vpi', 'ghdl')]
        self.ghdl.run(extra_args)
    

def main():
    goku = Goku.from_args(sys.argv[1:])
    goku.prepare()
    goku.compile()
    goku.run()


if __name__ == '__main__':
    main()
