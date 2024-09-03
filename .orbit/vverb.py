from mod import Command, Env, Generic, Blueprint, Hdl
import random
import sys
import os
import argparse

# Handle command-line arguments
parser = argparse.ArgumentParser(prog='vverb', allow_abbrev=False)

parser.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level verilog parameters')

parser.add_argument('--log', action='store', default='events.log', help='specify the log file path written during simulation')
parser.add_argument('--skip-model', action='store_true', help='skip execution of a design model (if exists)')
parser.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
parser.add_argument('--loop-limit', action='store', type=int, default=10_000, help='specify the limit of tests before timing out')

args = parser.parse_args()

MAX_TESTS = int(args.loop_limit)
SKIP_MODEL = bool(args.skip_model)
GENERICS = args.generic
SEED = args.seed
EVENTS_LOG_FILE = str(args.log)

BENCH_NAME = Env.read('ORBIT_TB_NAME', missing_ok=False)
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

HAS_MODEL = py_model != None

if HAS_MODEL == True and SKIP_MODEL == False:
    ORBIT_TB = Env.read("ORBIT_TB_NAME", missing_ok=False)
    ORBIT_DUT = Env.read("ORBIT_DUT_NAME", missing_ok=False)

    # export the interfaces using orbit to get the json data format
    dut_data = Command("orbit").arg("get").arg(ORBIT_DUT).arg("--json").output()[0].strip()
    tb_data = Command("orbit").arg("get").arg(ORBIT_TB).arg("--json").output()[0].strip()

    Command("verb") \
        .arg("model") \
        .arg("--coverage").arg('coverage.txt') \
        .arg("--seed="+str(SEED) if SEED != None else None) \
        .arg("--loop-limit="+str(MAX_TESTS) if MAX_TESTS != None else None) \
        .arg("--dut").arg(dut_data) \
        .arg("--tb").arg(tb_data) \
        .args(['-g=' + item.to_str() for item in GENERICS]) \
        .arg("python") \
        .arg("--") \
        .arg(py_model) \
        .spawn() \
        .unwrap()
    pass

src_files = [str(src.path) for src in rtl_order]

# overwrite top level parameters using -G<name>=<value>
# verilator --binary -j 0 -Wall our.v
Command('verilator') \
    .arg('--binary') \
    .arg('--sv') \
    .args(['-j', '0']) \
    .args(['--Mdir', OUT_DIR]) \
    .args(['-o', BENCH_NAME]) \
    .args(src_files) \
    .spawn() \
    .unwrap()

# run the executable
Command(OUT_DIR + '/' + BENCH_NAME).spawn().unwrap()

# check the event log
if HAS_MODEL == True:
    Command('verb') \
        .arg('check') \
        .arg(EVENTS_LOG_FILE) \
        .arg("--coverage=coverage.txt" if os.path.exists('coverage.txt') else None) \
        .arg('--stats') \
        .spawn() \
        .unwrap()
    pass

exit(0)
