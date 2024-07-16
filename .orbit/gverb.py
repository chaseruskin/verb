# Project: Verb
# Target: gvert
# References: https://github.com/ghdl/ghdl
#
# Defines a common workflow for working with the GHDL simulator and software
# models written in Python used for generating test vector I/O. Generics
# are passed to the software script as well as the VHDL testbench for
# synchronization across code.
#
# The script is written to be used as the entry-point to an Orbit target.

import os, sys
import sys
import random
import argparse
from typing import List

from mod import Command, Status, Env, Generic, Blueprint, Hdl

# Set up environment and constants

BENCH = Env.read("ORBIT_BENCH", missing_ok=True)

# temporarily append ghdl path to PATH env variable
GHDL_PATH: str = Env.read("ORBIT_ENV_GHDL_PATH", missing_ok=True)
Env.add_path(GHDL_PATH)

# Handle command-line arguments

parser = argparse.ArgumentParser(prog='gvert', allow_abbrev=False)

parser.add_argument('--lint', action='store_true', default=False, help='run static analysis and exit')
parser.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level VHDL generics')
parser.add_argument('--std', action='store', default='93', metavar='EDITION', help="specify the VHDL edition (87, 93, 02, 08, 19)")
parser.add_argument('--relax', action='store_true', help='relax semantic rules for ghdl')
parser.add_argument('--exit-on', action='store', default='error', metavar='LEVEL', help='select severity level to exit on (default: error)')

parser.add_argument('--log', action='store', default='events.log', help='specify the log file path written during simulation')
parser.add_argument('--skip-model', action='store_true', help='skip execution of a design model (if exists)')
parser.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
parser.add_argument('--max-tests', action='store', type=int, default=10_000, help='specify the limit of tests before timing out')

args = parser.parse_args()

MAX_TESTS = int(args.max_tests)
SKIP_MODEL = bool(args.skip_model)
IS_RELAXED = bool(args.relax)
GENERICS: List[Generic] = args.generic
STD_VHDL = str(args.std)
SEED = args.seed
LINT_ONLY = bool(args.lint)
SEVERITY_LVL = str(args.exit_on)
EVENTS_LOG_FILE = str(args.log)

# Construct the options for GHDL
GHDL_OPTS = ['--ieee=synopsys', '--syn-binding']

GHDL_OPTS += ['--std='+STD_VHDL]

if IS_RELAXED == True:
    GHDL_OPTS += ['-frelaxed']

# Read blueprint

py_model: str = None
rtl_order: List[Hdl] = []
working_lib: str = ''
# collect data from the blueprint
for rule in Blueprint().parse():
    if rule.fileset == 'VHDL':
        rtl_order += [Hdl(rule.identifier, rule.path)]
        working_lib = rule.identifier
    elif rule.fileset == 'PYMDL':
        py_model = rule.path
    pass

HAS_MODEL = py_model != None

# Analyze VHDL source code

# analyze units
print("info: analyzing hdl source code ...")
item: Hdl
for item in rtl_order:
    print('  ->', Env.quote_str(item.path))
    Command('ghdl') \
        .arg('-a') \
        .args(GHDL_OPTS) \
        .args(['--work='+str(item.lib), item.path]) \
        .spawn() \
        .unwrap()
    pass


# halt workflow here when only providing lint
if LINT_ONLY == True:
    print("info: static analysis complete")
    exit(0)


# [STEP]: Run the design model to generate test vectors

if HAS_MODEL == True and SKIP_MODEL == False:
    import json

    ORBIT_TB = Env.read("ORBIT_BENCH", missing_ok=False)
    ORBIT_DUT = Env.read("ORBIT_DUT", missing_ok=False)

    # export the interfaces using orbit to get the json data format
    dut_data = Command("orbit").arg("get").arg(ORBIT_DUT).arg("--json").output()[0]
    tb_data = Command("orbit").arg("get").arg(ORBIT_TB).arg("--json").output()[0]

    tb_json = json.loads(tb_data)
    # modify the json data and set defaults
    for g in GENERICS:
        for tb_gen in tb_json['generics']:
            if tb_gen['identifier'].upper() == g.key.upper():
                tb_gen['default'] = str(g.val)
                pass
            pass
        pass

    tb_data = json.dumps(tb_json, separators=(',', ':'))

    # send environment variables for verb
    Env.write("VERTEX_DUT", dut_data.strip())
    Env.write("VERTEX_TB", tb_data.strip())

    Env.write("VERTEX_EVENTS_LOG", EVENTS_LOG_FILE)
    Env.write("VERTEX_COVERAGE_REPORT", 'coverage.txt')

    Env.write("VERTEX_RANDOM_SEED", SEED)
    Env.write("VERTEX_TEST_COUNT_LIMIT", MAX_TESTS)

    # or set these on the command-line of the verb tool

    import runpy, sys, os
    # Switch the sys.path[0] from this script's path to the model's path
    this_script_path = sys.path[0]
    sys.path[0] = os.path.dirname(py_model)
    print("info: running python software model ...")
    # run the python model script in its own namespace
    runpy.run_path(py_model, init_globals={})
    sys.path[0] = this_script_path
    pass


# Run the VHDL simulation

if BENCH is None:
    exit('error: no testbench to simulate\n\nhint: use \"--lint\" to only analyze the HDL code')

VCD_FILE = str(BENCH)+'.vcd'

print("info: starting hdl simulation for testbench", Env.quote_str(BENCH), "...")
status: Status = Command('ghdl') \
    .arg('-r') \
    .args(GHDL_OPTS) \
    .arg('--work='+working_lib) \
    .arg(BENCH) \
    .args(['--vcd='+VCD_FILE, '--assert-level='+SEVERITY_LVL]) \
    .args(['-g' + item.to_str() for item in GENERICS]) \
    .spawn(verbose=False)

status.unwrap()
print('info: simulation complete')
print("info: vcd file saved at:", os.path.join(os.getcwd(), VCD_FILE))

# Analyze results from runnning simulation

rc: int = 0

if HAS_MODEL == True:
    import verb
    # print("info: Simulation history saved at:", verb.log.get_event_log_path())
    print("info: analyzing results ...\n")

    print('--- coverage analysis summary ---')
    print(verb.coverage.summary())
    print('--- simulation analysis summary ---')
    print(verb.analysis.summary())

    print("info: coverage report saved at:", os.path.join(os.getcwd(), verb.coverage.report_path()))
    print("info: events log saved at:", os.path.join(os.getcwd(), EVENTS_LOG_FILE))

    print("info: coverage score:", verb.coverage.report_score())
    print("info: simulation score:", verb.analysis.report_score())

    rc = 0 if verb.analysis.check() == True and verb.coverage.check() == True else 101
    pass

exit(rc)
