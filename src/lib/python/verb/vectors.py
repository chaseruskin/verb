# Project: Verb
# Module: vectors
#
# A Vectors contains the test vectors for a particular model.

class Vectors:
    from .model import Mode
    from typing import List as _List

    def __init__(self, path: str, mode: Mode):
        '''
        Creates a trace file to write stimuli/results for a potential hardware simulation.
        
        ### Parameters
        - The `name` argument sets the file's path name
        - The `mode` argument determines which directional ports to capture when writing to the file
        '''
        import os
        from .model import Mode

        self._path = str(path)
        # try to decode str if provided as a string
        self._mode = mode if isinstance(mode, Mode) == True else Mode.from_str(str(mode))

        self._exists = os.path.exists(self._path)
        # clear the existing file
        if self._exists == True:
            open(self._path, 'w').close()
        # create the file if it does not exist
        elif self._exists == False:
            if len(os.path.dirname(self._path)) > 0:
                os.makedirs(os.path.dirname(self._path), exist_ok=True)
            open(self._path, 'w').close()
            self._exists = True
        
        self._is_empty = True
        self._file = None
        pass


    def __del__(self):
        if self._file != None:
            self._file.close()
        pass


    def __enter__(self):
        if self._file == None:
            self._file = open(self._path, 'a')
        return self
    

    def __exit__(self, exception_type, exception_value, exception_traceback):
        # handle any exceptions
        self._file.close()


    def open(self):
        '''
        Explicit call to obtain ownership of the file. It is the programmer's
        responsibility to close the file when done.

        Calling this function and leaving the file open while appending traces
        to the test vector files can improve performance when many writes are
        required.
        '''
        # open the file in append mode
        if self._file == None:
            self._file = open(self._path, 'a')
        return self
    

    def close(self):
        '''
        Explicit call to release ownership of the file. This operation is
        idempotent.
        '''
        if self._file != None:
            self._file.close()
            self._file = None
        return self


    def push(self, model, ignore_coverage: bool=False):
        '''
        Writes the directional ports of the bus funcitonal model to the test vector file.

        Format each signal as logic values in the file to be read in during
        simulation.

        The format uses commas (`,`) to separate different signals and the order of signals
        written matches the order of ports in the interface json data.

        Each value is written with a ',' after the preceeding value in the 
        argument list. A newline is formed after all arguments
        '''
        from .model import Signal, _extract_ports, _extract_signals, Mode
        from .coverage import CoverageNet, Coverage

        if self._file == None:
            raise Exception("failed to write to file " + str(self._path) + " due to not being open")
        
        info: Signal
        net: CoverageNet

        # ignore the name when collecting the ports for the given mode
        signals = [p[1] for p in _extract_ports(model, mode=self._mode)] + [p[1] for p in _extract_signals(model)]
        # check if there are coverages to automatically update
        if ignore_coverage == False:
            for net in Coverage.get_nets():
                if net.has_sink() == True:
                    # verify the observation involves only signals being written for this transaction
                    sinks = net.get_sink_list()
                    print(sinks)
                    for sink in sinks:
                        print(net._name)
                        print(sink._name, sink._mode)
                        print(signals)
                        # exit early if a signal being observed is not this transaction
                        if type(sink) == Signal and sink not in signals:
                            print('broken')
                            break
                        pass
                    # perform an observation if the signals are in this transaction
                    else:
                        net.check(net.get_sink())
                pass
            pass

        DELIM = ' '
        NEWLINE = '\n'

        open_in_scope: bool = self._file == None
        fd = self._file if open_in_scope == False else open(self._path, 'a')
        
        if self._is_empty == False:
            fd.write(NEWLINE)
        for info in signals:
            fd.write(str(info) + DELIM)

        self._is_empty = False

        # close the file if it was opened in this current scope
        if open_in_scope == True:
            fd.close()
        pass

    pass