from mod import Command, Env, Generic, Blueprint, Hdl
import random
import sys
import os
import argparse
import glob
import shutil

class Verilator:

    def __init__(self, args):
        self.out_dir = 'build'
        self.seed = args.seed
        self.max_tests = args.loop_limit
        self.skip_model = bool(args.skip_model)
        self.lint_only = bool(args.lint)
        self.use_vcd = bool(args.vcd)
        self.events_log_file = str(args.log)
        self.generics = args.generic
        self.macros = args.define
        self.line_coverage = bool(args.line_coverage)
    
    pass


def main():
    # Handle command-line arguments
    parser = argparse.ArgumentParser(prog='vsim', allow_abbrev=False)

    parser.add_argument('--lint', action='store_true', default=False, help='run static analysis and exit')
    parser.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level verilog parameters')
    parser.add_argument('--vcd', action='store_true', default=False, help='enable saving vcd from testbench')
    parser.add_argument('--line-coverage', action='store_true', default=False, help='enable line coverage')

    parser.add_argument('--log', action='store', default='events.log', help='specify the log file path written during simulation')
    parser.add_argument('--skip-model', action='store_true', help='skip execution of a design model (if exists)')
    parser.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
    parser.add_argument('--loop-limit', action='store', type=int, default=None, help='specify the limit of tests before timing out')

    parser.add_argument('--define', '-d', action='append', type=str, default=[], metavar='KEY[=VALUE]', help='set preprocessor defines')

    args = parser.parse_args()

    V = Verilator(args)

    py_model: str = None
    rtl_order = []

    # collect data from the blueprint
    for rule in Blueprint().parse():
        if rule.fileset == 'VLOG' or rule.fileset == 'SYSV':
            rtl_order += [Hdl(rule.identifier, rule.path)]
        elif rule.fileset == 'PYMDL':
            py_model = rule.path
        pass

    HAS_MODEL = py_model != None

    BENCH_NAME = Env.read('ORBIT_TB_NAME', missing_ok=False)

    IP_PATH = Env.read("ORBIT_MANIFEST_DIR", missing_ok=False)

    # format list of source files for verilator command-line
    src_files = [str(src.path) for src in rtl_order]

    # format generics for verilator command-line
    top_gens = ['-G'+str(g.key)+'='+str(g.val) for g in V.generics]
    top_macros = ['-D'+str(m) for m in V.macros]

    # only perform lint and exit
    if V.lint_only == True:
        Command('verilator') \
            .arg('--lint-only') \
            .arg('--sv') \
            .arg('--timing') \
            .args(['-j', '4']) \
            .args(top_gens) \
            .args(['--Mdir', V.out_dir]) \
            .arg('-Wall') \
            .arg('-I'+str(IP_PATH)) \
            .args(top_macros) \
            .args(src_files) \
            .spawn() \
            .unwrap()
        exit(0)

    if HAS_MODEL == True and V.skip_model == False:
        ORBIT_TB = Env.read("ORBIT_TB_NAME", missing_ok=False)
        ORBIT_DUT = Env.read("ORBIT_DUT_NAME", missing_ok=False)

        # export the interfaces using orbit to get the json data format
        dut_data = Command("orbit").arg("get").arg(ORBIT_DUT).arg("--json").output()[0].strip()
        tb_data = Command("orbit").arg("get").arg(ORBIT_TB).arg("--json").output()[0].strip()

        seed_arg = '' if V.seed == None else '--seed='+str(V.seed)
        loop_limit_arg = '' if V.max_tests == None else '--loop-limit='+str(V.max_tests)

        Command("verb") \
            .arg("model") \
            .arg("--coverage").arg('coverage.rpt') \
            .arg(seed_arg) \
            .arg(loop_limit_arg) \
            .arg("--dut").arg(dut_data) \
            .arg("--tb").arg(tb_data) \
            .args(['-g=' + item.to_str() for item in V.generics]) \
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
        .arg('--trace' if V.use_vcd == True else '') \
        .arg('--timing') \
        .args(['--timescale', '1ns/10ps']) \
        .args(['-j', '0']) \
        .arg('--coverage-line' if V.line_coverage else '') \
        .args(top_gens) \
        .arg('-I'+str(IP_PATH)) \
        .args(top_macros) \
        .args(['--Mdir', V.out_dir]) \
        .arg('-Wno-fatal') \
        .args(['-o', BENCH_NAME]) \
        .args(src_files) \
        .spawn() \
        .unwrap()

    # run the executable
    Command(V.out_dir + '/' + BENCH_NAME).spawn().unwrap()

    # annotate the line coverage
    if V.line_coverage == True:
        Command('verilator_coverage') \
            .arg('coverage.dat') \
            .arg('-annotate') \
            .arg('lines') \
            .arg('--annotate-all') \
            .spawn() \
            .unwrap()
        # rename all .sv files with a .cov extension to reduce confusion
        files = glob.glob('lines/**/*.sv', recursive=True)
        for f in files:
            shutil.move(f, f+'.cov')

    # check the event log
    if HAS_MODEL == True and os.path.exists(V.events_log_file) == True:
        Command('verb') \
            .arg('check') \
            .arg(V.events_log_file) \
            .args(["--coverage", "coverage.rpt"] if os.path.exists('coverage.rpt') else []) \
            .arg('--stats') \
            .spawn() \
            .unwrap()
        pass

    exit(0)


if __name__ == "__main__":
    main()
