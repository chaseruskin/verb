# Profile: Hyperspace Labs
# Module: mod.py
# 
# This module contains common low-level functions used across targets written 
# in Python.

import os
from typing import List, Tuple
from enum import Enum
import argparse
import shutil
import subprocess

class Esc:
    def __init__(self, inner: str):
        self._inner = inner

    def __str__(self):
        return str(self._inner)
    pass


class Tcl:
    def __init__(self, path: str):
        self._file: str = path
        self._data: str = ''
        self._indent: int = 0
        pass

    def push(self, code, end='\n', raw=False):
        if raw == True:
            self._data += ('  '*self._indent) + code
        else:
            for c in code:
                self._data += ('  '*self._indent)
                if isinstance(c, Esc) == True:
                    self._data += str(c) + ' '
                else:
                    self._data += "\"" + str(c) + "\"" + ' '
            pass
        self._data += end
        pass

    def save(self):
        with open(self._file, 'w') as f:
            f.write(self._data)
        pass

    def indent(self):
        self._indent += 1

    def dedent(self):
        self._indent -= 1
        if self._indent < 0:
            self._indent = 0
        pass

    def get_path(self) -> str:
        return self._file
    pass


class Env:
    @staticmethod
    def quote_str(s: str) -> str:
        '''Wraps the string `s` around double quotes `\"` characters.'''
        return '\"' + s + '\"'

    @staticmethod
    def read(key: str, default: str=None, missing_ok: bool=True) -> None:
        try:
            value = os.environ[key]
        except KeyError:
            value = None
        # do not allow empty values to trigger variable
        if value is not None and len(value) == 0:
            value = None
        if value is None:
            if missing_ok == False:
                exit("error: environment variable "+Env.quote_str(key)+" does not exist")
            else:
                value = default
        return value

    @staticmethod
    def write(key: str, value: str):
        os.environ[key] = str(value)

    @staticmethod
    def add_path(path: str) -> bool:
        if path is not None and os.path.exists(path) and path not in os.getenv("PATH"):
            os.environ["PATH"] += os.pathsep + path
            return True
        return False
    pass


class Fileset(Enum):
    Vhdl = 0,
    Verilog = 1,
    SystemVerilog = 2,
    Undefined = 'e'

    def __init__(self, value):
        self._value = value


    @staticmethod
    def from_str(s: str):
        s = str(s).upper()
        if s == 'VHDL':
            return Fileset.Vhdl
        if s == 'VLOG':
            return Fileset.Verilog
        if s == 'SYSV':
            return Fileset.SystemVerilog
        fset = Fileset.Undefined
        return fset
    pass


class Step:
    def __init__(self, fset: str, lib: str, path: str):
        self.fset = str(fset).upper()
        self._fset_variant = Fileset.from_str(fset)
        self.lib = lib
        self.path = path
        pass

    def is_builtin(self) -> bool:
        return self._fset_variant == Fileset.Vhdl or \
            self._fset_variant == Fileset.Verilog or \
            self._fset_variant == Fileset.SystemVerilog
    
    def is_set(self, fset) -> bool:
        if isinstance(fset, Fileset):
            return self._fset_variant == fset
        return self.fset == str(fset).upper()
    
    def is_aux(self, fset: str) -> bool:
        return self.fset == str(fset).upper()

    def is_vhdl(self) -> bool:
        return self._fset_variant == Fileset.Vhdl
    
    def is_vlog(self) -> bool:
        return self._fset_variant == Fileset.Verilog
    
    def is_sysv(self) -> bool:
        return self._fset_variant == Fileset.SystemVerilog
    
    pass


class Blueprint:
    def __init__(self):
        self._file = Env.read("ORBIT_BLUEPRINT", missing_ok=False)
        pass

    def parse(self) -> List[Step]:
        rules = []
        # read each line of the blueprint to parse the rules
        with open(self._file, 'r') as blueprint:
            for rule in blueprint.readlines():
                # remove newline and split into three components
                fileset, identifier, path = rule.strip().split('\t')
                rules += [Step(fileset, identifier, path)]
                pass
            pass
        return rules

    pass


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
            msg = "generic "+Env.quote_str(s)+" is missing <value>"
            raise argparse.ArgumentTypeError(msg)
        return result

    def to_str(self) -> str:
        return self.key+'='+self.val
    
    def __str__(self):
        return self.key+'='+self.val
    
    pass


class Status(Enum):
    OKAY = 0
    FAIL = 101
    pass

    @staticmethod
    def from_int(code: int):
        if code == 0:
            return Status.OKAY
        else:
            return Status.FAIL

    def unwrap(self):
        # print an error message
        if self == Status.FAIL:
            exit(Status.FAIL.value)
        pass

    def __int__(self):
        return int(self.value)
    pass


class Command:
    def __init__(self, command: str):
        self._command = shutil.which(command)
        self._args = []

    def args(self, args: List[str]):
        if args is not None and len(args) > 0:
            self._args += args
        return self
    
    def arg(self, arg: str):
        # skip strings that are empty
        if arg is not None and str(arg) != '':
            self._args += [str(arg)]
        return self
    
    def spawn(self, verbose: bool=False) -> Status:
        job = [self._command] + self._args
        if verbose == True:
            command_line = self._command
            for c in self._args:
                command_line += ' ' + Env.quote_str(c)
            print('info:', command_line)
        child = subprocess.Popen(job)
        status = child.wait()
        return Status.from_int(status)

    def output(self, verbose: bool=False) -> Tuple[str, Status]:
        job = [self._command] + self._args
        # display the command being executed
        if verbose == True:
            command_line = self._command
            for c in self._args:
                command_line += ' ' + Env.quote_str(c)
            print('info:', command_line)
        # execute the command and capture channels for stdout and stderr
        try:
            pipe = subprocess.Popen(job, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            print('error: command not found: \"'+self._command+'\"')
            return ('', Status.FAIL)
        out, err = pipe.communicate()
        if err is not None:
            return (err.decode('utf-8'), Status.FAIL)
        if out is not None:
            return (out.decode('utf-8'), Status.OKAY)
        return ('', Status.OKAY)
    pass
