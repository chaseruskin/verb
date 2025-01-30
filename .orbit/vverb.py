from mod import Command, Env, Generic, Blueprint, Hdl
import random
import sys
import os
import argparse

# Handle command-line arguments
parser = argparse.ArgumentParser(prog='vverb', allow_abbrev=False)

parser.add_argument('--lint', action='store_true', default=False, help='run static analysis and exit')
parser.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level verilog parameters')
parser.add_argument('--vcd', action='store_true', default=False, help='enable saving vcd from testbench')

parser.add_argument('--log', action='store', default='events.log', help='specify the log file path written during simulation')
parser.add_argument('--skip-model', action='store_true', help='skip execution of a design model (if exists)')
parser.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
parser.add_argument('--loop-limit', action='store', type=int, default=None, help='specify the limit of tests before timing out')

parser.add_argument('--define', '-d', action='append', type=str, default=[], metavar='KEY[=VALUE]', help='set preprocessor defines')

args = parser.parse_args()

SEED = args.seed
MAX_TESTS = args.loop_limit
SKIP_MODEL = bool(args.skip_model)
GENERICS = args.generic
LINT_ONLY = bool(args.lint)
USE_VCD = bool(args.vcd)
EVENTS_LOG_FILE = str(args.log)
MACROS = args.define

OUT_DIR = 'build'

py_model: str = None
rtl_order = []
working_lib: str = ''
# collect data from the blueprint
for rule in Blueprint().parse():
    if rule.fileset == 'VLOG' or rule.fileset == 'SYSV':
        rtl_order += [Hdl(rule.identifier, rule.path)]
        working_lib = rule.identifier
    elif rule.fileset == 'PYMDL':
        py_model = rule.path
    pass

# format list of source files for verilator command-line
src_files = [str(src.path) for src in rtl_order]

# format generics for verilator command-line
top_gens = ['-G'+str(g.key)+'='+str(g.val) for g in GENERICS]
top_macros = ['-D'+str(m) for m in MACROS]

IP_PATH = Env.read("ORBIT_MANIFEST_DIR", missing_ok=False)

# only perform lint and exit
if LINT_ONLY == True:
    Command('verilator') \
        .arg('--lint-only') \
        .arg('--sv') \
        .arg('--timing') \
        .args(['-j', '0']) \
        .args(top_gens) \
        .args(['--Mdir', OUT_DIR]) \
        .arg('-Wall') \
        .arg('-I'+str(IP_PATH)) \
        .args(top_macros) \
        .args(src_files) \
        .spawn() \
        .unwrap()
    exit(0)

HAS_MODEL = py_model != None

BENCH_NAME = Env.read('ORBIT_TB_NAME', missing_ok=False)

if HAS_MODEL == True and SKIP_MODEL == False:
    ORBIT_TB = Env.read("ORBIT_TB_NAME", missing_ok=False)
    ORBIT_DUT = Env.read("ORBIT_DUT_NAME", missing_ok=False)

    # export the interfaces using orbit to get the json data format
    dut_data = Command("orbit").arg("get").arg(ORBIT_DUT).arg("--json").output()[0].strip()
    tb_data = Command("orbit").arg("get").arg(ORBIT_TB).arg("--json").output()[0].strip()

    seed_arg = '' if SEED == None else '--seed='+str(SEED)
    loop_limit_arg = '' if MAX_TESTS == None else '--loop-limit='+str(MAX_TESTS)

    Command("verb") \
        .arg("model") \
        .arg("--coverage").arg('coverage.txt') \
        .arg(seed_arg) \
        .arg(loop_limit_arg) \
        .arg("--dut").arg(dut_data) \
        .arg("--tb").arg(tb_data) \
        .args(['-g=' + item.to_str() for item in GENERICS]) \
        .arg("python") \
        .arg("--") \
        .arg(py_model) \
        .spawn() \
        .unwrap()
    pass

# overwrite top level parameters using -G<name>=<value>
# verilator --binary -j 0 -Wall our.v
Command('verilator') \
    .arg('--binary') \
    .arg('--sv') \
    .arg('--trace' if USE_VCD == True else '') \
    .arg('--timing') \
    .args(['-j', '0']) \
    .args(top_gens) \
    .arg('-I'+str(IP_PATH)) \
    .args(top_macros) \
    .args(['--Mdir', OUT_DIR]) \
    .arg('-Wno-fatal') \
    .args(['-o', BENCH_NAME]) \
    .args(src_files) \
    .spawn() \
    .unwrap()

# run the executable
Command(OUT_DIR + '/' + BENCH_NAME).spawn().unwrap()

# check the event log
if HAS_MODEL == True and os.path.exists(EVENTS_LOG_FILE) == True:
    Command('verb') \
        .arg('check') \
        .arg(EVENTS_LOG_FILE) \
        .arg("--coverage=coverage.txt" if os.path.exists('coverage.txt') else None) \
        .arg('--stats') \
        .spawn() \
        .unwrap()
    pass

exit(0)
