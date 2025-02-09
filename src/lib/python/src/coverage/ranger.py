from .net import CoverageNet

class CoverRange(CoverageNet):
    """
    A `CoverRange` is designed to track a span of integer numbers, which can divided up among steps.
    This structure is similar to a `CoverGroup`, however, the bins defined in a `CoverRange` are implicitly defined
    along the set of integers.
    """
    from ..model import Signal

    def get_type(self) -> str:
        """
        Returns the name of the coverage type.
        """
        return 'CoverRange'

    def __init__(self, name: str, span: range, goal: int=1, bypass: bool=False, max_steps: int=64, target=None, source=None, sink=None, advancer=None, checker=None):
        """
        Create a new `CoverRange` object.

        ### Parameters
        - `span`: specify the range of values to cover
        - `max_steps`: specify the maximum number of steps to cover the entire range
        - `advancer`: a function that accepts the `source` as an argument and returns an integer
        """
        import math

        self._domain = span

        self._count = 0
        self._goal = goal
        self._max_steps = max_steps

        # initialize the total count of all covers
        self._total_count = 0

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()
    
        # define a custom function that should return a boolean to define the targeted point
        self._fn_checker = checker
        self._fn_advancer = advancer

        # determine the step size
        self._step_size = self._domain.step
        num_steps_needed = int(abs(self._domain.stop - self._domain.start) / self._domain.step)
        self._step_size = self._domain.step
        # limit by computing a new step size
        # self._step_size = self._domain.step
        self._num_of_steps = num_steps_needed

        if self._max_steps != None and num_steps_needed > self._max_steps:
            # update instance attributes
            self._step_size = int(math.ceil(abs(self._domain.stop - self._domain.start) / self._max_steps))
            self._num_of_steps = self._max_steps
            pass

        self._table = [[]] * self._num_of_steps

        self._table_counts = [0] * self._num_of_steps
        # print('len', len(self._table_counts))
        # print(self._step_size)
        self._start = self._domain.start
        self._stop = self._domain.stop

        # verify the source is

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass

    def to_json_internal(self) -> dict:
        data = super().to_json()
        more_data = {
            'count': int(self.get_points_met()),
            'goal': int(self.get_total_goal_count()),
        }

        bins = []

        # print the coverage analysis
        for i, _ in enumerate(self._table):
            # collect a single bin
            if self._step_size > 1:
                step = str(i * self._step_size) + '..=' + str(((i+1) * self._step_size)-1)
            else:
                step = i
                pass
            count = int(self._table_counts[i])

            cur_bin = {
                'name': str(step),
                'met': None if self._bypass == True else count >= self._goal,
                'count': int(count),
                'goal': int(self._goal),
            }
            # get each hit that helped toward the current bin's goal
            hits = []
            if self._step_size > 1 and i in self._mapped_items.keys():
                seq = [(key, val) for key, val in self._mapped_items[i].items()]
                seq.sort()
                for (key, val) in seq:
                    cur_hit = {
                        'value': str(key),
                        'count': int(val)
                    }
                    hits += [cur_hit]
                    pass
            # update the current bin's account for its hits
            cur_bin['hits'] = hits
            # add to the bin list
            bins += [cur_bin]
            pass

        more_data['bins'] = bins
        data.update(more_data)
        return data

    def get_total_goal_count(self) -> int:
        return self._goal * int(len(self._table_counts))

    def get_goal(self) -> int:
        return self._goal * len(self._table_counts)

    def get_count(self) -> int:
        points_met = 0
        for entry in self._table_counts:
            if entry >= self._goal:
                points_met += 1
        return points_met

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

    def get_total_points_met(self) -> int:
        points_met = 0
        for entry in self._table_counts:
            points_met += entry
        return points_met
    
    def passed(self) -> bool:
        """
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        """
        for entry in self._table_counts:
            # exit early on first failure for not meeting coverage goal
            if entry < self._goal:
                return False
        return True

    def _transform(self, item):
        return int(item) if self._fn_checker == None else int(self._fn_checker(item))

    def is_in_sample_space(self, item) -> bool:
        mapped_item = self._transform(item)
        return mapped_item >= self._start and mapped_item < self._stop

    def _map_onto_range(self, item) -> int:
        if self.is_in_sample_space(item) == False:
            return None
        return self._transform(item)

    def check(self, item) -> bool:
        """
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        """
        # print(item)
        # print(self._stop)
        if self.is_in_sample_space(item) == False:
            return False
        # convert item to int
        mapped_item = self._transform(item)
        # print('mapped', mapped_item)
        # print(self._step_size)
        # transform into coverage domain
        index = int(mapped_item / self._step_size)
        # print('index', index, mapped_item/self._step_size)
        # caution: use this line when trying to handle very big ints that were mapped (fp inprecision?)
        if index >= len(self._table_counts):
            return False
        # check if it improves progessing by adding to a mapping that has not met the goal yet
        is_progress = self._table_counts[index] < self._goal
        # update the coverage for this value
        self._table[index] += [mapped_item]
        self._table_counts[index] += 1
        self._total_count += 1
        # track original items that count toward their space of the domain
        if index not in self._mapped_items.keys():
            self._mapped_items[index] = dict()
        # store the count of the integer value of the number for encounters tracking/stats
        if mapped_item not in self._mapped_items[index].keys():
            self._mapped_items[index][mapped_item] = 0 
        # increment the count of this item being detected
        self._mapped_items[index][mapped_item] += 1
        return is_progress
    
    def advance(self, rand: bool=False):
        """
        Returns the next item currently not meeting the coverage goal.

        Enabling `rand` will allow for a random item to be picked, rather than
        sequentially.

        Returns `None` if no item is left (all goals are reached and coverage is
        passing).
        """
        import random as _random
        from ..signal import Signal as _Signal

        # can only map 1-way (as of now)
        if self._fn_checker != None and self._fn_advancer == None:
            raise Exception("Cannot map back to original values")

        if self._fn_advancer != None:
            if isinstance(self._source, (list, tuple)) == True:
                self._fn_advancer(*self._source)
            else:
                self._fn_advancer(self._source)
            return
        
        available = []
        # filter out the elements who have not yet met the goal
        for i, count in enumerate(self._table_counts):
            if count < self._goal:
                available += [i]
            pass
        if len(available) == 0:
            return None

        next_value = None
        if rand == True:
            j = _random.choice(available)
            # transform back to the selection of the expanded domain space
            next_value = _random.randint(j * self._step_size, ((j+1) * self._step_size) - 1)
        else:
            # provide 1st available if random is disabled
            j = available[0]
            next_value = _random.randint(j * self._step_size, ((j+1) * self._step_size) - 1)
        # assign the next value for the source
        if isinstance(self._source, (list, tuple)) == True:
            self._source[0].set(next_value)
        # set if is of type signal
        elif isinstance(self._source, _Signal):
            self._source.set(next_value)
        # retun the value otherwise
        else:
            return next_value
    
    def to_string(self, verbose: bool) -> str:
        """
        Formats the relevant data into a string.
        """
        from . import _find_longest_str_len
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
            for i, _ in enumerate(self._table):
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
                    for i, (key, val) in enumerate(seq):
                        result += '\n        '
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