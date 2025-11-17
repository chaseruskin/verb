'''
Backend target process for simulations with GHDL + cocotb + verb.
'''

import argparse
import sys

from aquila import log
from aquila import env
from aquila.blueprint import Entry
from aquila.env import KvPair, Seed
from aquila.ghdl import Ghdl

from verb.orbit.coco import Cocotb
from verb.orbit.adverb import Verb

class Goku:
    '''
    Simulation workflow for GHDL + cocotb + verb.
    '''

    def __init__(self, ghdl: Ghdl, coco: Cocotb, verb: Verb):
        '''
        Construct a new Goku instance.
        '''
        self.ghdl = ghdl
        self.coco = coco
        self.verb = verb
        # attempt to generate a testbench if one is missing
        auto_tb_path = self.coco.generate_tb(ghdl.top_sim_name, ghdl.dut_path)
        if auto_tb_path is not None:
            ghdl.top_sim_name += '_tb'
            ghdl.entries += [Entry('VHDL', ghdl.top_sim_lib, auto_tb_path, [ghdl.entries[-1].path])]

    @staticmethod
    def from_args(args: list):
        '''
        Construct a new Goku instance from a set of arguments.
        '''
        parser = argparse.ArgumentParser('goku', allow_abbrev=False)

        parser.add_argument('--run', '-r', action='store', choices=Ghdl.MODES, default=Ghdl.SIM_MODE, help='the mode to run')
        parser.add_argument('--generic', '-g', action='append', type=KvPair.from_arg, default=[], metavar='KEY=VALUE', help='set top-level generics')
        parser.add_argument('--seed', metavar='NUM', action='store', default=Seed(), type=Seed.from_str, help='set random seed')
        parser.add_argument('--time-res', '-t', metavar='UNITS', default='ps', help='set the simulation time resolution')

        args = parser.parse_args(args)
        ghdl = Ghdl(
            mode=args.run,
            generics=args.generic,
            seed=args.seed,
            time_res=args.time_res,
        )
        return Goku(
            ghdl=ghdl,
            coco=Cocotb('COCOTB-PY', ghdl._seed, ghdl._time_res),
            verb=Verb(ghdl._generics)
        )
    
    def prepare(self):
        env.verify_all_generics_have_values(env.read('ORBIT_DUT_JSON'), self.ghdl._generics)
        if self.coco.get_test_mod() is None and self.ghdl._mode != 'com':
            log.error('cocotb test requires a python module to test')
        self.ghdl.prepare()

    def compile(self):
        self.ghdl.compile()

    def run(self):
        extra_args = ['--vpi='+self.coco.get_lib_name_path('vpi', 'ghdl')]
        self.ghdl.run(extra_args)
    

def main():
    goku = Goku.from_args(sys.argv[1:])
    goku.prepare()
    goku.compile()
    goku.run()


if __name__ == '__main__':
    main()
