# Project: Vertex
# Module: context
#
# Handles input/output interface between components outside of the library.

import os

class Runner:

    _current = None

    def __init__(self, context) -> None:
        import json, random
        self._context = context
        self._parameters = []
        self._ports = []
        # set the testbench generics
        with open(os.path.join(self._context._work_dir, self._context._tb_if_path), 'r') as fd:
            data = fd.read()
            self._parameters = json.loads(data)['generics']
        # set the design's ports
        with open(os.path.join(self._context._work_dir, self._context._dut_if_path), 'r') as fd:
            data = fd.read()
            self._ports = json.loads(data)['ports']
        # set the randomness seed
        random.seed(context._seed)
        pass


    def param(self, key: str, type=str):
        '''
        Accesses the generic based upon the provided `key`.

        Define a type to help with converting to a Python-friendly datatype, as all
        generics are initially stored as `str`.
        '''
        from . import cast
        # verify the key exists
        value: dict
        for param in self._parameters:
            if param['name'] == key:
                value = param['default']
                break
        else:
            all_keys = ''
            for param in self._parameters:
                all_keys += str(param['name']) + ', '
            if len(all_keys) > 0:
                all_keys = all_keys[:len(all_keys)-2]
            raise Exception('unknown parameter "'+key+'" (possible values: ' + all_keys + ')')
        if type == int:
            value = cast.from_vhdl_int(value)
        elif type == bool:
            value = cast.from_vhdl_bool(value)
        elif type == str:
            value = cast.from_vhdl_str(value)
        elif type == [int]:
            value = cast.from_vhdl_ints(value)
        elif type == [bool]:
            value = cast.from_vhdl_bools(value)
        elif type == [str]:
            value = cast.from_vhdl_strs(value)
        else:
            raise Exception('unsupported casting for generic "'+key+'" to type: ' + str(type))
        return value
    

    def port(self, key: str) -> dict:
        '''
        Finds the first index that has a port with a name equal to `key`.
        '''
        for port in self._ports:
            if port['name'] == key:
                return port
        return None
    

    def port_index(self, key: str) -> int:
        '''
        Returns the location of the port, if it exists. Returns -1 otherwise.
        '''
        for (i, port) in enumerate(self._ports):
            if port['name'] == key:
                return i
        return -1
    
    pass


class Context:

    def __init__(self) -> None:
        '''
        Create a new verification environment.
        '''
        self._built = False

        self._max_test_count = -1
        self._seed = None

        self._work_dir = os.getcwd()

        self._tb_if_path = None
        self._dut_if_path = None

        self._event_log = 'events.log'
        self._coverage_report = 'coverage.json'
        pass
    

    def tb_interface(self, path: str):
        '''
        Sets the path to the testbench interface json data.
        '''
        if self._built == True: return self
        self._tb_if_path = str(path)
        return self


    def dut_interface(self, path: str):
        '''
        Sets the path to the design-under-test's interface json data.
        '''
        if self._built == True: return self
        self._dut_if_path = str(path)
        return self
    

    def max_test_count(self, limit: int):
        '''
        Sets the maximum number of tests allowed to be tested before timing out.
        '''
        if self._built == True: return self
        self._max_test_count = int(limit)
        return self
    

    def seed(self, value: int):
        '''
        Sets the random number generation seed.
        '''
        if self._built == True: return self
        self._seed = int(value)
        return self


    def build(self) -> Runner:
        self._built = True
        Runner._current = Runner(self)
        return Runner._current
    

    def coverage_report(self, path: str):
        '''
        Sets the path of the coverage report file.
        '''
        if self._built == True: return self
        self._coverage_report = str(path)
        return self
    

    @staticmethod
    def current() -> Runner:
        '''
        Reference the current context being ran.
        '''
        return Runner._current
    
    pass
