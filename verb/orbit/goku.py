'''
Backend target process for simulations with GHDL + cocotb + verb.
'''

import argparse
import sys

from aquila import log
from aquila import env
from aquila import orbit
from aquila.orbit import Entry
from aquila.test import TestRunner, TestModule, Seed
from aquila.env import KvPair
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

    @staticmethod
    def from_args(args: list):
        '''
        Construct a new Goku instance from a set of arguments.
        '''
        parser = argparse.ArgumentParser('goku', allow_abbrev=False)

        parser.add_argument('--run', '-r', action='store', choices=Mode.choices(), default=Mode.SIM, help='the mode to run')
        parser.add_argument('--log', metavar='LEVEL', choices=LogLvl.choices(), default=LogLvl.INFO, help='set the messaging log level')
        parser.add_argument('--generic', '-g', action='append', type=KvPair.from_arg, default=[], metavar='KEY=VALUE', help='set top-level generics')
        parser.add_argument('--filter', '-f', action='store', default=None, type=str, help='apply a filter to which tests to run')
        parser.add_argument('--seed', metavar='NUM', action='store', default=Seed(), type=Seed.from_str, help='set random seed')
        parser.add_argument('--timescale', '-t', metavar='UNIT', default='ps', help='set the simulation time resolution')

        args = parser.parse_args(args)
        # compose the instances of this workflow
        ghdl = Ghdl(
            mode=Mode.from_arg(args.run),
            generics=KvPair.into_dict(args.generic),
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
        verb = Verb()
        return Goku(
            ghdl=ghdl,
            cocotb=cocotb,
            verb=verb
        )
    
    def prepare(self):
        self.ghdl.prepare()

    def configure(self, dut: str, tb: str, generics: dict, seed: int):
        self.cocotb.configure(dut, tb, seed)
        if self.cocotb.get_test_mod() is None and self.ghdl._mode != 'com':
            log.error('cocotb test requires a python module to test')
        self.verb.configure(dut, generics)
        self.ghdl.configure(dut, tb, dut, generics)

    def compile(self, top_path: str):
        self.ghdl.compile(top_path)

    def run(self, out_dir: str):
        extra_args = ['--vpi='+self.cocotb.get_lib_name_path('vpi', 'ghdl')]
        return self.ghdl.run(out_dir, extra_args)
    

def main():
    goku = Goku.from_args(sys.argv[1:])
    runner = TestRunner(
        default=TestModule(env.read('ORBIT_DUT_NAME'), env.read('ORBIT_TB_NAME'), goku.ghdl._generics)
    )

    tm: TestModule
    for tm in runner.get_modules():
        # verify all generics have known values
        top_json = orbit.get_unit_json(tm.get_top())
        orbit.verify_generics(top_json, tm.get_generics())
        tm.set_path(top_json['source'])

        # verify a seed is applied to this test
        if tm.get_seed() is None:
            tm.set_seed(Seed().get_seed())

        auto_tb_entry: Entry = goku.cocotb.generate_tb_entry(tm.get_dut(), tm.get_tb(), goku.ghdl.work_lib, 'benches')
        if auto_tb_entry is not None:
            tm.set_tb(tm.get_dut()+'_tb')
            goku.ghdl.entries += [auto_tb_entry]
            tm.set_path(auto_tb_entry.path)

    goku.prepare()

    runner.disp_start()
    tm: TestModule
    for tm in runner.get_modules():
        runner.disp_trial_start(tm)
        goku.configure(tm.get_dut(), tm.get_tb(), tm.get_generics(), tm.get_seed())
        goku.compile(tm.get_path())
        runner.disp_trial_progress()
        ok, msg = goku.run(tm.get_short_hash())
        runner.disp_trial_result(ok, msg)

    all_ok = runner.disp_result()
    if all_ok == False:
        exit(101)


if __name__ == '__main__':
    main()
