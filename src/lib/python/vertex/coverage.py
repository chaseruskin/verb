# Project: Vertex
# Module: coverage
#
# This module handles coverage implementations to track coverage nets: 
# CoverPoints, CoverRanges, CoverGroups, and CoverCrosses.

from abc import ABC as _ABC
from enum import Enum as _Enum

def _find_longest_str_len(x) -> int:
    '''
    Given a list `x`, determines the longest length str.
    '''
    longest = 0
    for item in x:
        if len(str(item)) > longest:
            longest = len(str(item))
    return longest


class Status(_Enum):
    PASSED = 0
    SKIPPED = 1
    FAILED = 2
    pass


class Coverage:
    
    _total_coverages = 0
    _passed_coverages = 0
    _goals_met = 0
    _total_points = 0
    _coverage_report = 'coverage.txt'

    @staticmethod
    def met(timeout: int=-1) -> bool:
        '''
        Checks if each coverage specification has met its goal.

        If a coverage specification is bypassed, it counts as meeting its
        goal. If the timeout is set to -1, it will be disabled and only return
        `True` once all cases are covered.
        '''
        from .context import Context
        if timeout == -1:
            timeout = Context.current()._context._max_test_count
        # force the simulation to pass if enough checks are evaluated
        if timeout > 0 and CoverageNet._counter >= timeout:
            # save the coverage report
            Coverage.save()
            return True        
        # check every cover-node
        cov: CoverageNet
        for cov in CoverageNet._group:
            if cov.skipped() == False and cov.passed() == False:
                # increment the counter
                CoverageNet._counter += 1
                return False
        Coverage.save()
        return True


    @staticmethod
    def get_nets():
        '''
        Returns the list of all coverage nets being tracked.
        '''
        return CoverageNet._group
    

    @staticmethod
    def get_failing_nets():
        '''
        Returns a list of coverage nets that have not met their coverage goal.

        This function excludes coverage nets that are bypassed.
        '''
        net: CoverageNet
        result = []
        for net in CoverageNet._group:
            # only append nets that are not bypassed and are not completed
            if net.skipped() == False and net.passed() == False:
                result += [net]
            pass
        return result


    @staticmethod
    def report(verbose: bool=True) -> str:
        '''
        Compiles a report of the coverage statistics and details. Setting `verbose`
        to `False` will only provide minimal details to serve as a quick summary.
        '''
        contents = ''
        cov: CoverageNet
        for cov in CoverageNet._group:
            contents += cov.log(verbose) + '\n'
        return contents
    

    @staticmethod
    def count() -> int:
        '''
        Returns the number of times the Coverage class has called the 'all_passed'
        function. If 'all_passed' is called once every transaction, then it gives
        a sense of how many test cases were required in order to achieve full
        coverage.
        '''
        return CoverageNet._counter
    

    @staticmethod
    def tally_score():
        '''
        Iterates through all CoverageNets to compute the ratio of pass/fail.
        '''
        Coverage._total_coverages = 0
        Coverage._passed_coverages = 0
        Coverage._goals_met = 0
        Coverage._total_points = 0
        net: CoverageNet
        for net in CoverageNet._group:
            if net.status() == Status.SKIPPED:
                continue
            Coverage._total_coverages += 1
            Coverage._goals_met += net.get_points_met()
            if type(net) == CoverPoint:
                Coverage._total_points += 1
            else:
                Coverage._total_points += net.get_partition_count()
            if net.status() == Status.PASSED:
                Coverage._passed_coverages += 1
            pass


    @staticmethod
    def percent() -> float:
        '''
        Return the percent of all coverages that met their goal. Each covergroup's bin
        is tallied individually instead of tallying the covergroup as a whole.

        Coverages that have a status of `SKIPPED` are not included in the tally.

        Returns `None` if there are no coverages to tally. The percent value is
        from 0.00 to 100.00 percent, with rounding to 2 decimal places.
        '''
        Coverage.tally_score()
        passed = Coverage._goals_met
        total = Coverage._total_points
        return round((passed/total) * 100.0, 2) if total > 0 else None


    @staticmethod
    def save() -> str:
        '''
        Saves the report if not already saved, and then returns the absolute path to the file.
        '''
        import os
        from . import context

        path = Coverage._coverage_report
        Coverage.tally_score()
        header = ''
        header += "Seed: " + str(context.Context.current()._context._seed) + '\n'
        header += "Iterations: " + str(Coverage.count()) + '\n'
        header += "Points covered: " + str(Coverage._goals_met) + '\n'
        header += "Total points: " + str(Coverage._total_points) + '\n'
        header += "Coverage: "   + str(Coverage.percent()) + ' %\n'
        with open(path, 'w') as f:
            # header
            f.write(header)
            f.write('\n')  
            # summary
            f.write(Coverage.report(False))
            f.write('\n')  
            # details
            f.write(Coverage.report(True))
            pass
        return os.path.abspath(path)


    @staticmethod
    def summary() -> str:
        return Coverage.report(False) + '\n' + \
            "Score: " + report_score()


def report_path() -> str:
    '''
    Returns the coverage report's filesystem path.
    '''
    return Coverage._coverage_report


def report_score() -> str:
    '''
    Formats the score as a `str`.
    '''
    Coverage.tally_score()
    return (str(Coverage.percent()) + ' % ' if Coverage.percent() != None else 'N/A ') + '(' + str(Coverage._goals_met) + '/' + str(Coverage._total_points) + ')'


def check(threshold: float=1.0) -> bool:
    '''
    Determines if coverage was met based on meeting or exceeding the threshold value.

    ### Parameters
    - `threshold` expects a floating point value [0, 1.0]
    '''
    Coverage.tally_score()
    passed = Coverage._goals_met
    total = Coverage._total_points
    if total <= 0:
        return True
    return float(passed/total) >= threshold


class CoverageNet(_ABC):
    '''
    A CoverageNet is a generic base class for any converage type.
    '''
    from abc import abstractmethod as _abstractmethod
    from .model import Signal, Mode

    _group = []
    _counter = 0

    def __init__(self, name: str, bypass: bool=False, target: Signal=None, source: Signal=None, sink: Signal=None):
        '''
        Initializes a CoverageNet object.

        If a `target` is defined and either a `source` or `sink` is undefined, then the net assumes the
        `target` is also the undefined `source` and/or undefined `sink`.

        ### Parameters
        - `name`: the user-friendly name for the net
        - `bypass`: skips the net when true
        - `target`: the signal(s) involved in advancing and checking the coverage
        - `source`: the signal(s) involved in advancing the coverage
        - `sink`: the signal(s) involved in checking the coverage
        '''
        self._name = name
        self._bypass = bypass

        # remember the signal(s) that are written to advance coverage
        self._source = target if source == None else source
        # remember the signal(s) that are read to check coverage
        self._sink = target if sink == None else sink
    
        CoverageNet._group += [self]
        pass

    
    def has_sink(self) -> bool:
        '''
        Checks if the net is configured with a set of signal(s) to read from
        to check coverage.
        '''
        return self._sink != None
    

    def has_source(self) -> bool:
        '''
        Checks if the net is configured with a set of signal(s) to write to
        to advance coverage.
        '''
        return self._source != None
    

    def get_sink_list(self):
        '''
        Returns an iterable object of the signals to be read for checking coverage.
        '''
        from .model import Signal 

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
        '''
        Returns an iterable object of the signals to be written for advancing coverage.
        '''
        from .model import Signal 

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
        '''
        Returns the object that has reading permissions to check coverage.
        '''
        return self._sink
    

    def get_source(self):
        '''
        Returns the object that has writing permissions to advance coverage.
        '''
        return self._source


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
    def cover(self, item) -> bool:
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

        It can be thought of as the inverse function to `cover(...)`.
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


    def skipped(self) -> bool:
        '''
        Checks if this coverage is allowed to be bypassed during simulation due
        to an external factor making it impossible to pass.
        '''
        return self._bypass 
    

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


class CoverPoint(CoverageNet):
    '''
    CoverPoints are designed to track when a single particular event occurs.
    '''
    from .model import Signal

    def __init__(self, name: str, goal: int=1, bypass=False, advance=None, cover=None, target: Signal=None, source: Signal=None, sink: Signal=None):
        '''
        Initialize a cover point object.

        ### Parameters
        - `advance`: a function or lambda expression that provides values to write to the source to advance coverage
        - `cover`: a function or lambda expression that provides a way to read values from a sink to check coverage
        '''
        self._count = 0
        self._goal = goal
        # define a custom function that should return a boolean to define the targeted point
        self._fn_cover = cover
        self._fn_advance = advance

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass


    def _transform(self, item):
        return item if self._fn_cover == None else self._fn_cover(item)


    def is_in_sample_space(self, item) -> bool:
        mapped_item = int(self._transform(item))
        return mapped_item >= 0 and mapped_item < 2
    

    def _map_onto_range(self, item) -> int:
        if self.is_in_sample_space(item) == False:
            return None
        return int(self._transform(item))
    

    def get_range(self) -> range:
        return range(0, 2, 1)
    

    def get_partition_count(self) -> int:
        return 2
    

    def get_points_met(self) -> int:
        '''
        Returns the number of points that have met their goal.
        '''
        return 1 if self._count >= self._goal else 0


    def cover(self, item):
        '''
        Returns `True` if the `cond` was satisfied and updates the internal count
        as the coverpoint tries to met or exceed its goal.
        '''
        if self.is_in_sample_space(item) == False:
            return False
        cond = bool(self._map_onto_range(item))
        if cond == True:
            self._count += 1
        return cond
    

    def advance(self, rand=False):
        return int(True) if self._fn_advance == None else self._fn_advance(self._source)


    def passed(self):
        return self._count >= self._goal
    

    def to_string(self, verbose: bool):
        return str(self._count) + '/' + str(self._goal)
    
    pass


class CoverGroup(CoverageNet):
    from typing import List as _List
    from .model import Signal

    group = []

    def __init__(self, name: str, bins: _List, goal: int=1, bypass: bool=False, max_bins=64, advance=None, cover=None, target: Signal=None, source: Signal=None, sink: Signal=None):
        '''
        Initialize a cover group object.

        ### Parameters
        - `advance`: a function or lambda expression that provides values to write to the source to advance coverage
        - `cover`: a function or lambda expression that provides a way to read values from a sink to check coverage
        '''
        # stores the items per index for each bin group
        self._macro_bins = []
        # stores the count for each bin
        self._macro_bins_count = []
        # store a hash to the index in the set of bins list
        self._bins_lookup = dict()

        # defining a bin range is more flexible for defining a large space

        # determine the number of maximum bins
        self._max_bins = max_bins

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()

        # will need to provide a division operation step before inserting into
        if len(bins) > self._max_bins:
            self._items_per_bin = int(len(bins) / self._max_bins)
        else:
            self._items_per_bin = 1

        # initialize the bins
        for i, item in enumerate(set(bins)):
            # items are already in their 'true' from from given input
            self._bins_lookup[int(item)] = i
            # group the items together based on a common index that divides them into groups
            i_macro = int(i / self._items_per_bin)
            if len(self._macro_bins) <= i_macro:
                self._macro_bins.append([])
                self._macro_bins_count.append(0)
                pass
            self._macro_bins[i_macro] += [int(item)]
            pass

        # set the goal required for each bin
        self._goal = goal
        # initialize the total count of all covers
        self._total_count = 0

        # store the function to map items into the coverage space
        self._fn_cover = cover
        # store the function to generate the proper values to advance coverage
        self._fn_advance = advance

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass


    def _transform(self, item):
        return int(item if self._fn_cover == None else self._fn_cover(item))


    def is_in_sample_space(self, item) -> bool:
        return self._bins_lookup.get(self._transform(item)) != None
    

    def _map_onto_range(self, item) -> int:
        if self.is_in_sample_space(item) == False:
            return None
        return int(self._bins_lookup[self._transform(item)])
    

    def get_range(self) -> range:
        return range(0, len(self._bins_lookup.keys()), self._items_per_bin)
    

    def get_partition_count(self) -> int:
        # the real number of partitions of the sample space
        return len(self._macro_bins)
    

    def _get_macro_bin_index(self, item) -> int:
        '''
        Returns the macro index for the `item` according to the bin division.
        '''
        return int(self._bins_lookup[item] / self._items_per_bin)
    

    def cover(self, item):
        '''
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        '''
        if self.is_in_sample_space(item) == False:
            return False
        # use special mapping function if defined
        mapped_item = self._transform(item)
        # got the item, but check its relative items under the same goal
        i_macro = self._get_macro_bin_index(mapped_item)
        # make the item exists as a possible entry and its macro goal is not met
        is_progress = self._macro_bins_count[i_macro] < self._goal
        # update the map with the value
        self._macro_bins_count[i_macro] += 1
        # update the total count
        self._total_count += 1
        # record the actual value that initiated this coverage
        if self._fn_cover != None:
            if i_macro not in self._mapped_items.keys():
                self._mapped_items[i_macro] = dict()
            if mapped_item not in self._mapped_items[i_macro].keys():
                self._mapped_items[i_macro][mapped_item] = 0 
            # increment the count of this item being detected
            self._mapped_items[i_macro][mapped_item] += 1
            pass
        return is_progress
    

    def get_points_met(self) -> int:
        points_met = 0
        for count in self._macro_bins_count:
            if count >= self._goal:
                points_met += 1
        return points_met
    

    def advance(self, rand=False):
        '''
        Returns the next item currently not meeting the coverage goal.

        Enabling `rand` will allow for a random item to be picked, rather than
        sequentially.

        Returns `None` if no item is left (all goals are reached and coverage is
        passing).
        '''
        import random as _random

        # can only map 1-way (as of now)
        if self._fn_cover != None and self._fn_advance == None:
            raise Exception("Cannot map back to original values")

        if self._fn_advance != None:
            raise Exception("Implement inverse mapping")
        
        available = []
        # filter out the elements who have not yet met the goal
        for i, count in enumerate(self._macro_bins_count):
            if count < self._goal:
                available += [i]
            pass
        if len(available) == 0:
            return None
        if rand == True:
            # pick a random macro bin
            i_macro = _random.choice(available)
            # select a random item from the bin
            return _random.choice(self._macro_bins[i_macro])

        # provide 1st available if random is disabled
        i_macro = available[0]
        return self._macro_bins[i_macro][0]

    
    def passed(self) -> bool:
        '''
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        '''
        for val in self._macro_bins_count:
            # fail on first failure
            if val < self._goal:
                return False
        return True
    

    def _macro_to_string(self, i) -> str:
        '''
        Write a macro_bin as a string.
        '''
        LIMITER = 7
        items = self._macro_bins[i]
        result = '['
        for i in range(0, 8):
            if i >= len(items):
                break
            result += str(items[i])
            if i < len(items)-1:
                result += ', '
            if i >= LIMITER:
                result += '...'
                break
            pass
        result += ']'
        return result


    def to_string(self, verbose: bool=False) -> str:
        result = ''
        # print each individual bin and its goal status
        if verbose == True:
            # determine the string formatting by identifying longest string
            longest_len = _find_longest_str_len([self._macro_to_string(i) for i, _ in enumerate(self._macro_bins)])
            is_first = True
            # print the coverage analysis
            for i, group in enumerate(self._macro_bins):
                if is_first == False:
                    result += '\n    '
                phrase = str(self._macro_to_string(i))
                count = self._macro_bins_count[i]
                result += str(phrase) + ': ' + (' ' * (longest_len - len(str(phrase)))) + str(count) + '/' + str(self._goal)
                # enumerate on all mapped values that were detected for this bin
                if self._fn_cover != None and i in self._mapped_items.keys() and self.get_range().step > 1:
                    # determine the string formatting by identifying longest string
                    sub_longest_len = _find_longest_str_len(self._mapped_items[i].keys())
                    seq = [(key, val) for key, val in self._mapped_items[i].items()]
                    seq.sort()
                    LIMITER = 20
                    for j, (key, val) in enumerate(seq):
                        result += '\n        '
                        if j > LIMITER:
                            result += '...'
                            break
                        result += str(key) + ': ' + (' ' * (sub_longest_len - len(str(key)))) + str(val)

                        pass
                is_first = False
        # print the number of bins that reached their goal
        else:
            bins_reached = 0
            for count in self._macro_bins_count:
                if count >= self._goal:
                    bins_reached += 1
                pass
            result += str(bins_reached) + '/' + str(len(self._macro_bins_count))
        return result
    pass


class CoverRange(CoverageNet):
    '''
    CoverRanges are designed to track a span of integer numbers, which can divided up among steps.
    This structure is similar to a CoverGroup, however, the bins defined in a CoverRange are implicitly defined
    along the set of integers.
    '''
    from .model import Signal

    def __init__(self, name: str, span: range, goal: int=1, bypass: bool=False, max_steps: int=64, advance=None, cover=None, target: Signal=None, source: Signal=None, sink: Signal=None):
        '''
        Initialize a cover range object. 
        
        ### Parameters
        - `advance`: a function or lambda expression that provides values to write to the source to advance coverage
        - `cover`: a function or lambda expression that provides a way to read values from a sink to check coverage
        '''
        import math

        domain = span
        self._goal = goal
        # domain = range
        # determine the step size
        self._step_size = domain.step
        self._max_steps = max_steps
        num_steps_needed = len(domain)
        # limit by computing a new step size
        self._step_size = domain.step
        self._num_of_steps = num_steps_needed
        if self._max_steps != None and num_steps_needed > self._max_steps:
            # update instance attributes
            self._step_size = int(math.ceil(abs(domain.start - domain.stop) / self._max_steps))
            self._num_of_steps = self._max_steps
            pass

        self._table = [[]] * self._num_of_steps
        self._table_counts = [0] * self._num_of_steps

        self._start = domain.start
        self._stop = domain.stop

        # initialize the total count of all covers
        self._total_count = 0

        # store a potential custom mapping function
        self._fn_cover = cover
        self._fn_advance = advance

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass


    def get_range(self) -> range:
        return range(self._start, self._stop, self._step_size)
    

    def get_partition_count(self) -> int:
        return self._num_of_steps
    

    def get_points_met(self) -> int:
        points_met = 0
        for entry in self._table_counts:
            if entry >= self._goal:
                points_met += 1
        return points_met
    

    def passed(self) -> bool:
        '''
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        '''
        for entry in self._table_counts:
            # exit early on first failure for not meeting coverage goal
            if entry < self._goal:
                return False
        return True
    

    def _transform(self, item):
        return int(item) if self._fn_cover == None else int(self._fn_cover(item))


    def is_in_sample_space(self, item) -> bool:
        mapped_item = self._transform(item)
        return mapped_item >= self._start and mapped_item < self._stop
    

    def _map_onto_range(self, item) -> int:
        if self.is_in_sample_space(item) == False:
            return None
        return self._transform(item)


    def cover(self, item) -> bool:
        '''
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        '''
        if self.is_in_sample_space(item) == False:
            return False
        # convert item to int
        mapped_item = self._transform(item)
        # transform into coverage domain
        index = int(mapped_item / self._step_size)
        # check if it improves progessing by adding to a mapping that has not met the goal yet
        is_progress = self._table_counts[index] < self._goal
        # update the coverage for this value
        self._table[index] += [mapped_item]
        self._table_counts[index] += 1
        self._total_count += 1
        # track original items that count toward their space of the domain
        if index not in self._mapped_items.keys():
            self._mapped_items[index] = dict()
        if item not in self._mapped_items[index].keys():
            self._mapped_items[index][mapped_item] = 0 
        # increment the count of this item being detected
        self._mapped_items[index][mapped_item] += 1
            
        return is_progress
    

    def advance(self, rand: bool=False):
        '''
        Returns the next item currently not meeting the coverage goal.

        Enabling `rand` will allow for a random item to be picked, rather than
        sequentially.

        Returns `None` if no item is left (all goals are reached and coverage is
        passing).
        '''
        import random as _random

        # can only map 1-way (as of now)
        if self._fn_cover != None and self._fn_advance == None:
            raise Exception("Cannot map back to original values")

        if self._fn_advance != None:
            raise Exception("Implement")
        
        available = []
        # filter out the elements who have not yet met the goal
        for i, count in enumerate(self._table_counts):
            if count < self._goal:
                available += [i]
            pass
        if len(available) == 0:
            return None
        if rand == True:
            j = _random.choice(available)
            # transform back to the selection of the expanded domain space
            expanded_space = [(j * self._step_size) + x for x in range(0, self._step_size)]
            # select a random item from the bin
            return _random.choice(expanded_space)
        # provide 1st available if random is disabled
        expanded_space = [(available[0] * self._step_size) + x for x in range(0, self._step_size)]
        return expanded_space[0]
    

    def to_string(self, verbose: bool) -> str:
        result = ''
        # print each individual bin and its goal status
        if verbose == True:
            # determine the string formatting by identifying longest string
            if self._step_size > 1:
                longest_len = len(str((len(self._table)-2) * self._step_size) + '..=' + str((len(self._table)-1) * self._step_size))
            else:
                longest_len = len(str(self._stop-1))
            is_first = True
            # print the coverage analysis
            for i, _group in enumerate(self._table):
                if is_first == False:
                    result += '\n    '
                if self._step_size > 1:
                    step = str(i * self._step_size) + '..=' + str(((i+1) * self._step_size)-1)
                else:
                    step = i
                count = self._table_counts[i]
                result += str(step) + ': ' + (' ' * (longest_len - len(str(step)))) + str(count) + '/' + str(self._goal)
                # determine the string formatting by identifying longest string
                if self._step_size > 1 and i in self._mapped_items.keys():
                    sub_longest_len = _find_longest_str_len(self._mapped_items[i].keys())
                    seq = [(key, val) for key, val in self._mapped_items[i].items()]
                    seq.sort()
                    LIMITER = 20
                    for i, (key, val) in enumerate(seq):
                        result += '\n        '
                        if i > LIMITER:
                            result += '...'
                            break
                        result += str(key) + ': ' + (' ' * (sub_longest_len - len(str(key)))) + str(val)
                        pass
                is_first = False
            pass
        # print the number of bins that reached their goal
        else:
            goals_reached = 0
            for count in self._table_counts:
                if count >= self._goal:
                    goals_reached += 1
                pass
            result += str(goals_reached) + '/' + str(len(self._table_counts))
        return result


class CoverCross(CoverageNet):
    '''
    CoverCrosses are designed to track cross products between two or more coverage nets.

    Internally, a CoverCross stores a CoverRange for the 1-dimensional flatten version of
    the N-dimensional cross product across the different coverage nets.
    '''
    from typing import List as _List

    def __init__(self, name: str, nets: _List[CoverageNet], goal: int=1, bypass=False):
        self._nets = nets[::-1]
        self._crosses = len(self._nets)
        
        combinations = 1
        for n in nets:
            combinations *= n.get_partition_count()
            pass

        self._inner = CoverRange(
            name,
            span=range(combinations),
            goal=goal,
            bypass=bypass,
            max_steps=None,
            cover=None,
            advance=None,
        )

        net: CoverageNet

        sink = []
        for net in self._nets:
            # cannot auto-check coverage if a sink is not defined
            if net.has_sink() == False:
                sink = None
                break
            sink += [net.get_sink()]
            pass

        source = []
        for net in self._nets:
            # cannot auto-advance coverage if a source is not defined
            if net.has_source() == False:
                source = None
                break
            source += [net.get_source()]
            pass

        # remove that entry and use this instance
        self._group.pop()
        # overwrite the entry with this instance in the class-wide data structure
        super().__init__(name=name, bypass=bypass, source=source, sink=sink, target=None)
        pass
    
    
    def get_sink_list(self):
        if hasattr(self, "_sink_list") == True:
            return self._sink_list
        
        self._sink_list = []
        
        net: CoverageNet
        for net in self._nets:
            self._sink_list += net.get_sink_list()

        return self._sink_list


    def get_source_list(self):
        if hasattr(self, "_source_list") == True:
            return self._source_list
        
        self._source_list = []
        
        net: CoverageNet
        for net in self._nets:
            self._source_list += net.get_source_list()

        return self._source_list


    def advance(self, rand=False):
        index = self._inner.advance(rand)
        # convert the 1-dimensional value into its n-dimensional value
        item = self._pack(index)
        # print(index, '->', item)

        i = self._flatten(item)
        # print(item, '->', i)

        # expand to the entire parition space for each element
        for i, net in enumerate(self._nets):
            item[i] *= net.get_range().step

        # print(index, '->', item)
        # exit('implement!')
        return item


    def get_range(self) -> range:
        return self._inner.get_range()
    

    def get_partition_count(self) -> int:
        return self._inner.get_partition_count()
    

    def is_in_sample_space(self, item) -> bool:
        for i, x in enumerate(item[::-1]):
            if self._nets[i].is_in_sample_space(x) == False:
                return False
        return True

    
    def get_cross_count(self) -> int:
        '''
        Returns the number of elements are involved in the cartesian cross product.
        '''
        return self._crosses
    

    def _pack(self, index):
        '''
        Packs a 1-dimensional index into a N-dimensional item.
        '''
        # initialize the set of values to store in the item
        item = [0] * self.get_cross_count()

        subgroup_sizes = [1] * self.get_cross_count()

        for i in range(self.get_cross_count()):
            subgroup_sizes[i] = self._nets[i].get_partition_count()
            for j in range(i+1, self.get_cross_count()):
                subgroup_sizes[i] *= self._nets[i].get_partition_count()
            pass

        subgroup_sizes = subgroup_sizes[::-1]
        # print(subgroup_sizes)
        # perform counting sequence and perform propery overflow/handling of the carry
        for i in range(0, index):
            item[0] += 1
            carry = True
            if item[0] >= subgroup_sizes[0]:
                item[0] = 0
            else:
                carry = False
            j = 1
            while carry == True and j < self.get_cross_count():
                item[j] += 1
                if item[j] >= subgroup_sizes[j]:
                    item[j] = 0
                else:
                    carry = False
                j += 1
                pass

        return item
    

    def _flatten(self, item):
        '''
        Flattens a N-dimensional item into a 1-dimensional index.

        Reference: 
        - https://stackoverflow.com/questions/7367770/how-to-flatten-or-index-3d-array-in-1d-array
        '''
        if len(item) != self.get_cross_count():
            raise Exception("Expects "+str(self._crosses)+" values in pair")
        index = 0
        # dimensions go: x, y, z... so reverse the tuple/list
        for i, x in enumerate(item[::-1]):
            # exit if an element was not a possible value
            if self._nets[i].is_in_sample_space(x) == False:
                return None
            y = self._nets[i]._map_onto_range(x)
            # collect all above partition sizes
            acc_step_counts = 1
            for j in range(i+1, self.get_cross_count()):
                acc_step_counts *= self._nets[j].get_partition_count()
            index += acc_step_counts * int(y / self._nets[i].get_range().step)
        return index


    def _map_onto_range(self, item):
        return self._flatten(item)
    

    def get_points_met(self) -> int:
        '''
        Returns the number of points that have met their goal.
        '''
        return self._inner.get_points_met()


    def cover(self, item):
        if self.is_in_sample_space(item) == False:
            return None
        index = self._flatten(item)
        return self._inner.cover(index)


    def passed(self):
        return self._inner.passed()
    

    def to_string(self, verbose: bool):
        return self._inner.to_string(verbose)

    pass


import unittest as _ut

class __Test(_ut.TestCase):

    def test_cross_flatten_2d(self):
        cross = CoverCross('test', [CoverRange('a', span=range(0, 4)), CoverRange('b', span=range(0, 4))])
        self.assertEqual(0, cross._flatten((0, 0)))
        self.assertEqual(3, cross._flatten((3, 0)))
        self.assertEqual(4, cross._flatten((0, 1)))
        self.assertEqual(5, cross._flatten((1, 1)))
        self.assertEqual(15, cross._flatten((3, 3)))
        pass

    def test_cross_flatten_3d(self):
        cross = CoverCross('test', [CoverRange('a', span=range(0, 2)), CoverRange('b', span=range(0, 3)), CoverRange('c', span=range(0, 4))])
        self.assertEqual(0, cross._flatten((0, 0, 0)))
        self.assertEqual(1, cross._flatten((1, 0, 0)))
        self.assertEqual(2*1, cross._flatten((0, 1, 0)))
        self.assertEqual(2*2, cross._flatten((0, 2, 0)))
        self.assertEqual(6, cross._flatten((0, 0, 1)))
        self.assertEqual(1 + 2 + 6, cross._flatten((1, 1, 1)))
        self.assertEqual(1 + 2*2 + 3*6, cross._flatten((1, 2, 3)))
        pass

    pass