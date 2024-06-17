# Project: Vertex
# Module: context
#
# Handles input/output interface between components outside of the library.


def param(key: str, type=str):
    '''
    Accesses the generic based upon the provided `key`.

    Define a type to help with converting to a Python-friendly datatype, as all
    generics are initially stored as `str`.
    '''
    from . import cast
    # verify the key exists
    value: dict
    for param in Context.current()._parameters:
        if param['name'] == key:
            value = param['default']
            break
    else:
        all_keys = ''
        for param in Context.current()._parameters:
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


def port(key: str) -> dict:
    '''
    Finds the first index that has a port with a name equal to `key`.
    '''
    for port in Context.current()._ports:
        if port['name'] == key:
            return port
    return None


class Runner:

    _current = None
    _locked = False

    def __init__(self, context) -> None:
        import json, random
        self._context = context
        self._parameters = []
        self._ports = []
        # set the testbench generics
        if self._context._bench_if != None:
            self._parameters = json.loads(self._context._bench_if)['generics']
        # set the design's ports
        if self._context._top_if != None:
            self._ports = json.loads(self._context._top_if)['ports']
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
    

    def param_index(self, key: str) -> int:
        for (i, param) in enumerate(self._parameters):
            if param['name'] == key:
                return i
        return -1


    def port_index(self, key: str) -> int:
        '''
        Returns the location of the port, if it exists. Returns -1 otherwise.
        '''
        for (i, port) in enumerate(self._ports):
            if port['name'] == key:
                return i
        return -1
    

    def override_param(self, key: str, value: str) -> str:
        '''
        Sets the parameter value and will replace any existing value.
        '''
        param = self._parameters[self.param_index(key)]
        if param == None:
            return None
        stale = param['default']
        param['default'] = str(value)
        return stale
    

    def override_port(self, key: str, value: str) -> str:
        '''
        Sets the port value and will replace any existing value.
        '''
        port = self._ports[self.port_index(key)]
        if port == None:
            return None
        stale = port['default']
        port['default'] = str(value)
        return stale
    pass


class Context:

    def __init__(self) -> None:
        '''
        Create a new verification environment.
        '''
        import os as _os
        
        self._built = False

        self._max_test_count = -1
        self._seed = None

        self._work_dir = _os.getcwd()

        self._bench_if = None
        self._top_if = None

        self._event_log = 'events.log'
        self._coverage_report = 'coverage.txt'
        pass

    def bench_interface(self, data: str):
        '''
        Sets the path to the testbench interface json data.
        '''
        if self._built == True: return self
        self._bench_if = str(data)
        return self


    def top_interface(self, data: str):
        '''
        Sets the path to the design-under-test's interface json data.
        '''
        if self._built == True: return self
        self._top_if = str(data)
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
        self._seed = value
        return self

    def lock(self) -> Runner:
        self._built = True
        if Runner._locked == False:
            Runner._current = Runner(self)
            Runner._locked = True
        return Runner._current
    
    def build(self) -> Runner:
        self._built = True
        if Runner._locked == False:
            Runner._current = Runner(self)
        return Runner._current

    def coverage_report(self, path: str):
        '''
        Sets the path of the coverage report file.
        '''
        if self._built == True: return self
        self._coverage_report = str(path)
        return self

    def event_log(self, path: str):
        '''
        Sets the path of the coverage report file.
        '''
        if self._built == True: return self
        self._event_log = str(path)
        return self

    @staticmethod
    def current() -> Runner:
        '''
        Reference the current context being ran.
        '''
        return Runner._current
    
    pass
