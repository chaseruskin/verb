# Project: Vertex
# Script: main.py
#
# Provides an interface between client and veriti as a command-line application.

import argparse


def tab(n: int) -> str:
    TAB_SIZE = 2
    return (' ' * TAB_SIZE) * n


class Generic:

    def __init__(self, key: str, val: str):
        self.key = key
        self.val = val
        pass
    pass


    @classmethod
    def from_str(self, s: str):
        # split on equal sign
        words = s.split('=', 1)
        if len(words) != 2:
            return None
        return Generic(words[0], words[1])
    

    @classmethod
    def from_arg(self, s: str):
        result = Generic.from_str(s)
        if result is None:
            msg = "Generic "+'\"' + s + '\"'+" is missing <value>"
            raise argparse.ArgumentTypeError(msg)
        return result


    def to_str(self) -> str:
        return self.key+'='+self.val
    
    pass


def main():
    import random, sys
    parser = argparse.ArgumentParser(prog='vertex', allow_abbrev=False)
    parser.add_argument('--version', action='version', version='0.1.0')
    exit(0)

#     sub_parsers = parser.add_subparsers(dest='subcommand', metavar='command')

#     # subcommand: 'make'
#     parser_make = sub_parsers.add_parser('make', help='create HDL code synchronized to the model')

#     parser_make.add_argument('--bfm', action='store_true', default=False, help='generate the HDL bus functional model')
#     parser_make.add_argument('--send', action='store_true', default=False, help='generate the HDL sending procedure')
#     parser_make.add_argument('--score', action='store_true', default=False, help='generate the HDL scoring procedure')
#     parser_make.add_argument('json', type=str, help='JSON data defining design-under-test\'s interface')

#     # subcommand: 'read'
#     parser_read = sub_parsers.add_parser('read', help='analyze post-simulation logged outcomes')

#     parser_read.add_argument('--log', type=str, required=True, help='path to log file')
#     parser_read.add_argument('--level', type=int, default=log.Level.WARN.value, help='severity level')

#     # subcommand: 'check'
#     parser_check = sub_parsers.add_parser('check', help='verify post-simulation logged outcomes')

#     parser_check.add_argument('--log', type=str, help='path to log file')
#     parser_check.add_argument('--cov', type=str, help='path to coverage file')
#     parser_check.add_argument('--work-dir', action='store', type=str, metavar='PATH', help='set the working directory')

#     # subcommand: 'run'
#     parser_run = sub_parsers.add_parser('run', help='execute the software model')

#     parser_run.add_argument('script', action='store', type=str, help='path to the python model script')
#     parser_run.add_argument('--generic', '-g', action='append', type=Generic.from_arg, default=[], metavar='KEY=VALUE', help='override top-level HDL generics')
#     parser_run.add_argument('--seed', action='store', type=int, nargs='?', default=None, const=random.randrange(sys.maxsize), metavar='NUM', help='set the randomness seed')
#     parser_run.add_argument('--if', dest='design_if', action='store', type=str, metavar='JSON', help='interface data for the design-under-test')
#     parser_run.add_argument('--tb-if', dest='bench_if', action='store', type=str, metavar='JSON', help='interface data for the testbench')
#     parser_run.add_argument('--work-dir', action='store', type=str, metavar='PATH', help='set the working directory')

#     args = parser.parse_args()
    
#     # branch on subcommand
#     sc = args.subcommand
#     if sc == 'make':
#         make(args)
#     elif sc == 'read':
#         data = log.read(args.log, args.level)
#         print(data)
#     elif sc == 'check':
#         rc = check(args)
#         exit(rc)
#         pass
#     elif sc == 'run':
#         run(args)
#     elif sc == None:
#         parser.print_help()
#         pass
#     pass


# def check(args: argparse.Namespace):
#     config.set(work_dir=args.work_dir, sim_log=args.log, cov_report=args.cov)
#     result = log.check() # and coverage.check()
#     # print('info:', 'Simulation history available at:', log.get_event_log_path(args.log))
#     # print('info:', log.report_score(args.log))
#     if result == True:
#         print('info:', 'Passed verification')
#         return 0
#     if result == False:
#         print('error:', 'Failed verification')
#         return 101


# def run(args: argparse.Namespace):
#     # initialize the state of veriti
#     config.set(design_if=args.design_if, bench_if=args.bench_if, work_dir=args.work_dir, seed=args.seed, generics=args.generic)
#     import runpy
#     # run the python model script in its own namespace
#     runpy.run_path(args.script, init_globals={})
#     pass


# def make(args: argparse.Namespace):
#     import json
#     # process the json data
#     design_if = json.loads(args.json)

#     # when creating driver and scorer, also grab list of port names (in their assembled order)
#     # so it synchronizes with which bit is which each line
#     # ... requires knowledge of the BFM defined in the SW model script
#     # or when writing tests in SW model, load the json data so it can get proper order from file

#     zero_raised = args.bfm == False and args.send == False and args.score == False
#     # create a function/command to take in a log file and coverage file to perform post-simulation analysis
#     # and provide a meaningful exit code and messages
#     if args.bfm == True or zero_raised == True:
#         print(get_vhdl_record_bfm(design_if['ports'], design_if['entity']))
#     if args.send == True or zero_raised == True:
#         print(get_vhdl_process_inputs(design_if['ports']))
#     if args.score == True or zero_raised == True:
#         print(get_vhdl_process_outputs(design_if['ports'], design_if['entity']))
#     pass


# def get_vhdl_process_inputs(ports):
#     '''
#     Generates valid VHDL code snippet for the reading procedure to parse the
#     respective model and its signals in the correct order as they are going
#     to be written to the corresponding test vector file.

#     This procedure assumes the package veriti is already in scope.
#     '''

#     body = ''
#     for p in ports:
#         if p['mode'].lower() != 'in':
#             continue
#         body += tab(2) + VHDL_DRIVER_PROC_NAME + '(row, bfm.'+p['name']+');\n'
#         pass

#     result = '''\
# procedure send_transaction(file fd: text) is
# ''' + tab(1) + '''variable row: line;
# begin
# ''' + tab(1) + '''if endfile(fd) = false then
# ''' + tab(2) + '''readline(fd, row);
# ''' + body + \
# tab(1) + '''end if;
# end procedure;'''
#     return result


# def get_vhdl_process_outputs(ports, entity) -> str:
#     '''
#     Generates valid VHDL code snippet for the reading procedure to parse the
#     respective model and its signals in the correct order as they are going
#     to be written to the corresponding test vector file.

#     This procedure assumes the package veriti is already in scope.
#     '''
#     body = ''
#     for p in ports:
#         if p['mode'].lower() != 'out':
#             continue
#         body += tab(2) + VHDL_LOADER_PROC_NAME + '(row, expct.'+p['name']+');\n'
#         body += tab(2) + VHDL_ASSERT_PROC_NAME + '(events, bfm.'+p['name']+', expct.'+p['name']+', \"'+p['name']+'\");\n'
#         pass

#     result = '''\
# procedure score_transaction(file fd: text) is 
# ''' + tab(1) + '''variable row: line;
# ''' + tab(1) + '''variable expct: '''+entity+'''_bfm;
# begin
# ''' + tab(1) + '''if endfile(fd) = false then
# ''' + tab(2) + '''readline(fd, row);
# ''' + body + \
# tab(1) + '''end if;
# end procedure;'''

#     return result
    

# def get_vhdl_record_bfm(ports, entity) -> str:
#     # determine spacing for neat alignment of signals
#     longest_len = 0
#     for item in ports:
#         id = str(item['name'])
#         if len(id) > longest_len:
#             longest_len = len(id)
#         pass

#     body = ''
#     # write each signal to the bfm record
#     for item in ports:
#         id = str(item['name'])
#         dt = str(item['type'])
#         _spacing = (' ' * (longest_len-len(id))) + ' '
#         body += tab(1) + id + ': ' + dt + ';\n'
#         pass
#     result = '''\
# type '''+entity+'''_bfm is record
# ''' + body + \
# '''end record;

# signal bfm: '''+entity+'''_bfm;
# '''    

#     return result


# if __name__ == '__main__':
#     main()
#     pass