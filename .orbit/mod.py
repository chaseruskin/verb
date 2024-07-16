# Project: Verb
# Module: mod.py
# 
# This module contains common low-level functions used across plugins written 
# in Python.

import os
from typing import List, Tuple
from enum import Enum
import argparse
import subprocess

class Env:
    @staticmethod
    def quote_str(s: str) -> str:
        '''Wraps the string `s` around double quotes `\"` characters.'''
        return '\"' + s + '\"'


    @staticmethod
    def read(key: str, default: str=None, missing_ok: bool=True) -> None:
        value = os.environ.get(key)
        # do not allow empty values to trigger variable
        if value is not None and len(value) == 0:
            value = None
        if value is None:
            if missing_ok == False:
                exit("error: Environment variable "+Env.quote_str(key)+" does not exist")
            else:
                value = default
        return value
    

    @staticmethod
    def write(key: str, value: str):
        if value != None:
            os.environ[key] = str(value)
        pass


    @staticmethod
    def add_path(path: str) -> bool:
        if path is not None and os.path.exists(path) and path not in os.getenv("PATH"):
            os.environ["PATH"] += os.pathsep + path
            return True
        return False
    pass


class Hdl:
    def __init__(self, lib: str, path: str):
        self.lib = lib
        self.path = path
        pass
    pass


class Rule:
    def __init__(self, fileset, identifier, path):
        self.fileset = fileset
        self.identifier = identifier
        self.path = path
        pass
    pass


class Blueprint:
    def __init__(self):
        blueprint_name = Env.read("ORBIT_BLUEPRINT", missing_ok=False)
        self._file = blueprint_name
        pass


    def parse(self) -> List[Rule]:
        rules = []
        # read each line of the blueprint to parse the rules
        with open(self._file, 'r') as blueprint:
            for rule in blueprint.readlines():
                # remove newline and split into three components
                fileset, identifier, path = rule.strip().split('\t')
                rules += [Rule(fileset, identifier, path)]
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
            msg = "Generic "+Env.quote_str(s)+" is missing <value>"
            raise argparse.ArgumentTypeError(msg)
        return result


    def to_str(self) -> str:
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
    pass


class Command:
    def __init__(self, command: str):
        self._command = command
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