from abc import ABC as _ABC

class CoverageNet(_ABC):
    """
    A `CoverageNet` is a generic base class inherited by any type of coverage.
    """
    from abc import abstractmethod as _abstractmethod
    from ..model import Signal, Mode
    from typing import List, Union

    # Class variable to track all created nets during modeling
    _group = []
    _counter = 0

    def __init__(self, name: str, bypass: bool=False, target=None, source=None, sink=None):
        """
        Create a new `CoverageNet` object.

        ### Parameters
        - `bypass`: Skips this net when trying to meet coverage if set to true
        - `target`: The signal(s) involved in advancing and checking this net's coverage
        - `source`: The signal(s) involved in advancing the net's coverage
        - `sink`:  The signal(s) involved in checking the net's coverage

        The `target` can be a single Signal or an iterable number of Signals. It
        is considered the `source` and `sink` (both read and written).

        The `source` acts as inputs that can be written to when to when trying to advance coverage to a
        scenario that would help approach its goal.

        The `sink` acts as the outputs that are read when checking if this net covered.
        """
        self._name = name
        self._bypass = bypass

        if target != None and (source != None or sink != None):
            raise Exception("Cannot specify source or sink while target is defined")
        # set the target
        if len(target) == 1:
            self._target = target[0]
        else:
            self._target = tuple(target)
        # set the source
        if source == None:
            self._source = self._target
        elif len(source) == 1:
            self._source = source[0]
        else:
            self._source = tuple(source)
        # set the sink
        if sink == None:
            self._sink = self._target
        elif len(sink) == 1:
            self._sink = sink[0]
        else:
            self._sink = tuple(sink)

        # add to the list to track
        CoverageNet._group += [self]
        pass

    @_abstractmethod
    def get_goal(self) -> int:
        """
        Returns the number of hits that must occur in order to be considered "covered".
        """
        pass

    @_abstractmethod
    def get_count(self) -> int:
        """
        Returns the current number of hits counted toward reaching the defined goal.
        """
        pass

    @_abstractmethod
    def get_type(self) -> str:
        """
        Returns the name of the coverage type.
        """

    def to_json(self) -> dict:
        """
        Formats the coverage net into a json-friendly data structure
        """
        data = {
            'name': self._name,
            'type': self.get_type(),
            'met': None if self._bypass == True else self.passed()
        }
        data.update(self.to_json_internal())

    def has_sink(self) -> bool:
        """
        Checks if the net is configured with a set of signal(s) to read from
        to check coverage.
        """
        return self._sink != None
    
    def has_source(self) -> bool:
        """
        Checks if the net is configured with a set of signal(s) to write to
        to advance coverage.
        """
        return self._source != None

    def get_sink_list(self):
        """
        Returns an iterable object of the signals to be read for checking coverage.
        """
        from ..model import Signal 

        if hasattr(self, '_sink_list') == True:
            return self._sink_list
        
        self._sink_list = []
        if self.has_sink() == True:
            # transform single signal into a list
            if type(self._sink) == Signal:
                self._sink_list = [self._sink]
            else:
                self._sink_list = list(self._sink)
            pass
        return self._sink_list

    def get_source_list(self):
        """
        Returns an iterable object of the signals to be written for advancing coverage.
        """
        from ..model import Signal 

        if hasattr(self, '_source_list') == True:
            return self._source_list
        
        self._source_list = []
        if self.has_source() == True:
            # transform single signal into a list
            if type(self._source) == Signal:
                self._source_list = [self._source]
            else:
                self._source_list = list(self._source)
            pass
        return self._source_list

    def get_sink(self):
        """
        Returns the object that has reading permissions to check coverage.
        """
        return self._sink

    def get_source(self):
        """
        Returns the object that has writing permissions to advance coverage.
        """
        return self._source
    
    def skipped(self) -> bool:
        """
        Checks if this coverage is allowed to be bypassed during simulation due
        to an external factor making it impossible to pass.
        """
        return self._bypass 

    @_abstractmethod
    def get_range(self) -> range:
        '''
        Returns a range object of the sample space and the size of each partitioning.
        '''
        pass
    
    @_abstractmethod
    def get_partition_count(self) -> int:
        '''
        Returns the number of unique partitions required to cover the entire sample space.
        '''
        pass

    @_abstractmethod
    def get_total_goal_count(self) -> int:
        '''
        Returns the number of total goals that must be reached by this net.
        '''
        pass

    @_abstractmethod
    def get_total_points_met(self) -> int:
        '''
        Returns the number of total points collected by this net.
        '''
        pass

    @_abstractmethod
    def is_in_sample_space(self, item) -> bool:
        '''
        Checks if the `item` is in the defined sample space.
        '''
        pass
    
    @_abstractmethod
    def _map_onto_range(self, item) -> int:
        '''
        Converts the `item` into a valid number within the defined range of possible values.
        
        If there is no possible mapping, return None.
        '''
        pass

    @_abstractmethod
    def check(self, item) -> bool:
        '''
        This function accepts either a single object or an interable object that is
        required to read to see if coverage proceeds toward its goal.

        It can be thought of as the inverse function to `advance(...)`.
        '''
        pass

    @_abstractmethod
    def advance(self, rand=False):
        '''
        This function returns either a single object or an iterable object that is
        required to be written to make the coverage proceed toward its goal.

        It can be thought of as the inverse function to `check(...)`.
        '''
        pass

    @_abstractmethod
    def get_points_met(self) -> int:
        '''
        Returns the number of points that have met their goal.
        '''
        pass

    @_abstractmethod
    def passed(self) -> bool:
        '''
        Returns `True` if the coverage met its goal.
        '''
        pass

    def log(self, verbose: bool=True) -> str:
        '''
        Convert the coverage into a string for user logging purposes. Setting `verbose` to `True`
        will provide more details in the string contents.
        '''
        label = 'CoverPoint' 
        if issubclass(type(self), CoverGroup):
            label = 'CoverGroup'
        elif issubclass(type(self), CoverRange):
            label = 'CoverRange'
        elif issubclass(type(self), CoverCross):
            label = 'CoverCross'
        elif issubclass(type(self), CoverPoint):
            label = 'CoverPoint'
        else:
            raise Exception("Unsupported CoverageNet "+str(type(self)))
        if verbose == False:
            return label + ": " + self._name + ': ' + self.to_string(verbose) + ' ...'+str(self.status().name)
        else:
            return label + ": " + self._name + ':' + ' ...'+str(self.status().name) + '\n    ' + self.to_string(verbose)

    def status(self) -> Status:
        '''
        Determine the status of the Coverage node.
        '''
        if self.skipped() == True:
            return Status.SKIPPED
        elif self.passed() == True:
            return Status.PASSED
        else:
            return Status.FAILED  

    @_abstractmethod
    def to_string(self, verbose: bool) -> str:
        '''
        Converts the coverage into a string for readibility to the end-user.
        '''
        pass
        
    pass