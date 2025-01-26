# Profile: Hyperspace Labs
# Target: msim
# Reference: https://www.microsemi.com/document-portal/doc_view/131617-modelsim-reference-manual
# 
# Runs ModelSim in batch mode to perform HDL simulations.

from mod import Env, Generic, Command, Blueprint, Step
from typing import List
import os
import argparse
import sys
import random

def main():
    # append modelsim installation path to PATH env variable
    Env.add_path(Env.read("ORBIT_ENV_MODELSIM_PATH", missing_ok=True))

    # handle command-line arguments
    parser = argparse.ArgumentParser(prog='msim', allow_abbrev=False)

    parser.add_argument('--lint', action='store_true', default=False, help='run static code analysis and exit')
    parser.add_argument('--stop-at-sim', action='store', help='stop after setting up the simulation')
    parser.add_argument('--gui', action='store_true', default=False, help='open the gui')
    parser.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
    parser.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level VHDL generics')
    parser.add_argument('--top-config', default=None, help='define the top-level configuration unit')
    parser.add_argument('--loop-limit', action='store', type=int, default=10_000, help='specify the limit of tests before timing out')

    args = parser.parse_args()

    # set up environment and constants
    TB_NAME = Env.read("ORBIT_TB_NAME", missing_ok=True)

    DO_FILE = 'orbit.do'
    WAVEFORM_FILE = 'vsim.wlf'

    # testbench's VHDL configuration unit
    TOP_LEVEL_CONFIG = args.top_config

    OPEN_GUI = bool(args.gui)
    STOP_AT_SIM = bool(args.stop_at_sim)
    LINT_ONLY = bool(args.lint)
    SEED = args.seed
    MAX_TESTS = int(args.loop_limit)

    GENERICS: List[Generic] = args.generic


    tb_do_file: str = None
    compile_order: List[Step] = []

    step: Step
    py_model: str = None
    # process blueprint
    for step in Blueprint().parse():
        if step.is_builtin() == True:
            compile_order += [step]
        if step.is_aux('DO'):
            tb_do_file = step.path
            pass
        if step.is_aux('PYMDL'):
            py_model = step.path
        pass

    HAS_MODEL = py_model != None

    print("info: compiling HDL source code ...")
    libraries = []
    work_lib = 'work'
    lib_args = []
    # compile hdl source code
    for step in compile_order:
        print('  ->', Env.quote_str(step.path))
        # create new libraries and their mappings
        if step.lib not in libraries:
            Command('vlib').arg(step.lib).spawn().unwrap()
            Command('vmap').arg(step.lib).arg(step.lib).spawn().unwrap()
            libraries.append(step.lib)
            lib_args += ['-L', step.lib]
        # compile source code
        if step.is_vhdl():
            Command('vcom').arg('-work').arg(step.lib).arg(step.path).spawn().unwrap()
        elif step.is_vlog():
            Command('vlog').arg('-work').arg(step.lib).arg(step.path).args(lib_args).spawn().unwrap()
        elif step.is_sysv():
            Command('vlog').arg('-sv').arg('-work').arg(step.lib).arg(step.path).args(lib_args).spawn().unwrap()
        # the last file to write the library is the working library
        work_lib = step.lib
        pass

    if LINT_ONLY == True:
        print("info: static analysis complete")
        exit(0)

    # run the design model
    if HAS_MODEL == True:
        ORBIT_TB = Env.read("ORBIT_TB_NAME", missing_ok=False)
        ORBIT_DUT = Env.read("ORBIT_DUT_NAME", missing_ok=False)

        # export the interfaces using orbit to get the json data format
        dut_data = Command("orbit").arg("get").arg(ORBIT_DUT).arg("--json").output()[0].strip()
        tb_data = Command("orbit").arg("get").arg(ORBIT_TB).arg("--json").output()[0].strip()

        status = Command("verb") \
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
            .spawn()
        
        status.unwrap()
        pass

    # prepare the simulation
    if TB_NAME is None:
        print('error: cannot proceed any further without a testbench\n\nhint: stop here using \"--lint\" to exit safely or set a testbench to run a simulation')
        exit(101)

    # create a .do file to automate modelsim actions
    print("info: generating .do file ...")
    with open(DO_FILE, 'w') as file:
        # prepend .do file data
        if OPEN_GUI == True:
            # add custom waveform/vsim commands
            if tb_do_file != None and os.path.exists(tb_do_file) == True:
                print("info: importing commands from .do file:", tb_do_file)
                with open(tb_do_file, 'r') as do:
                    for line in do.readlines():
                        # add all non-blank lines
                        if len(line.strip()) > 0:
                            file.write(line)
                    pass
            # write default to include all signals into waveform
            else:
                file.write('add wave *\n')
                pass
        if STOP_AT_SIM == False:
            file.write('run -all\n')
        if OPEN_GUI == False:
            file.write('quit\n')
        pass

    # determine to run as script or as gui
    mode = "-batch" if OPEN_GUI == False else "-gui"

    # override bench with top-level config
    TB_NAME = str(TOP_LEVEL_CONFIG) if TOP_LEVEL_CONFIG != None else str(TB_NAME)

    # reference: https://stackoverflow.com/questions/57392389/what-is-vsim-command-line
    print("info: starting simulation for testbench", Env.quote_str(TB_NAME), "...")
    Command('vsim') \
        .arg(mode) \
        .arg('-onfinish').arg('stop') \
        .arg('-do').arg(DO_FILE) \
        .arg('-wlf').arg(WAVEFORM_FILE) \
        .arg('-work').arg(work_lib) \
        .arg('+nowarn3116') \
        .arg(TB_NAME) \
        .args(['-g' + item.to_str() for item in GENERICS]) \
        .spawn() \
        .unwrap()

    # analyze the results from the simulation
    if HAS_MODEL == True:
        status = Command('verb') \
            .arg('check') \
            .arg('events.log') \
            .arg("--coverage=coverage.txt" if os.path.exists('coverage.txt') else None) \
            .arg('--stats') \
            .spawn()
        
        status.unwrap()
    pass


if __name__ == '__main__':
    main()
