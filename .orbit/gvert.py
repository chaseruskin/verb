# Project: Vertex
# Plugin: gvert
# References: https://github.com/ghdl/ghdl
#
# Defines a common workflow for working with the GHDL simulator and software
# models written in Python used for generating test vector I/O. Generics
# are passed to the software script as well as the VHDL testbench for
# synchronization across code.
#
# The script is written to be used as the entry-point to an Orbit plugin.

import os, sys
import sys
import random
import argparse
from typing import List

from mod import Command, Status, Env, Generic, Blueprint, Hdl

# [STEP]: Set up environment and constants

# directory to store artifacts within build directory
SIM_DIR = os.path.splitext(os.path.basename(__file__))[0]

BENCH: str = Env.read("ORBIT_BENCH", missing_ok=True)

# temporarily append ghdl path to PATH env variable
GHDL_PATH: str = Env.read("ORBIT_ENV_GHDL_PATH", missing_ok=True)
Env.add_path(GHDL_PATH)

# [STEP]: Handle command-line arguments

parser = argparse.ArgumentParser(prog='gsim', allow_abbrev=False)

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
GHDL_OPTS = ['--ieee=synopsys']

GHDL_OPTS += ['--std='+STD_VHDL]

if IS_RELAXED == True:
    GHDL_OPTS += ['-frelaxed']

# [STEP]: Read blueprint

py_model: str = None
rtl_order: List[Hdl] = []
# collect data from the blueprint
for rule in Blueprint().parse():
    if rule.fileset == 'VHDL-RTL' or rule.fileset == 'VHDL-SIM':
        rtl_order += [Hdl(rule.identifier, rule.path)]
    elif rule.fileset == 'PY-MODEL':
        py_model = rule.path
    pass

HAS_MODEL = py_model != None

# [STEP]: Analyze VHDL source code

# enter GHDL simulation working directory
os.makedirs(SIM_DIR, exist_ok=True)
os.chdir(SIM_DIR)

# analyze units
print("info: analyzing HDL source code ...")
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
    import vertex

    ORBIT_BENCH = Env.read("ORBIT_BENCH", missing_ok=False)
    ORBIT_TOP = Env.read("ORBIT_TOP", missing_ok=False)

    # export the interfaces using orbit to get the json data format
    top_if = Command("orbit").arg("get").arg(ORBIT_TOP).arg("--json").output()[0]
    bench_if = Command("orbit").arg("get").arg(ORBIT_BENCH).arg("--json").output()[0]

    vertex.context.Context() \
        .coverage_report('coverage.txt') \
        .event_log(EVENTS_LOG_FILE) \
        .bench_interface(bench_if) \
        .top_interface(top_if) \
        .max_test_count(MAX_TESTS) \
        .seed(SEED) \
        .lock()
    
    # update all parameters that were set on the command-line
    for g in GENERICS:
        vertex.context.Context.current().override_param(g.key, g.val)
        pass

    import runpy, sys, os
    # Switch the sys.path[0] from this script's path to the model's path
    this_script_path = sys.path[0]
    sys.path[0] = os.path.dirname(py_model)
    print("info: running Python software model ...")
    # run the python model script in its own namespace
    runpy.run_path(py_model, init_globals={})
    sys.path[0] = this_script_path
    pass


# [STEP]: Run the VHDL simulation

if BENCH is None:
    exit('error: no testbench to simulate\n\nhint: use \"--lint\" to only analyze the HDL code')

VCD_FILE = str(BENCH)+'.vcd'

print("info: starting VHDL simulation for testbench", Env.quote_str(BENCH), "...")
status: Status = Command('ghdl') \
    .arg('-r') \
    .args(GHDL_OPTS) \
    .args([BENCH, '--vcd='+VCD_FILE, '--assert-level='+SEVERITY_LVL]) \
    .args(['-g' + item.to_str() for item in GENERICS]) \
    .spawn(verbose=False)

status.unwrap()
print('info: simulation complete')
print("info: vcd file saved at:", os.path.join(os.getcwd(), VCD_FILE))

# [STEP]: Analyze results from runnning simulation

rc: int = 0

if HAS_MODEL == True:
    # print("info: Simulation history saved at:", vertex.log.get_event_log_path())
    print("info: analyzing results ...\n")

    print('--- coverage analysis summary ---')
    print(vertex.coverage.summary())
    print('--- simulation analysis summary ---')
    print(vertex.analysis.summary())

    print("info: coverage report saved at:", os.path.join(os.getcwd(), vertex.coverage.report_path()))
    print("info: events log saved at:", os.path.join(os.getcwd(), EVENTS_LOG_FILE))

    print("info: coverage score:", vertex.coverage.report_score())
    print("info: simulation score:", vertex.analysis.report_score())

    rc = 0 if vertex.analysis.check() == True and vertex.coverage.check() == True else 101
    pass

exit(rc)
