from .net import CoverageNet

class CoverPoint(CoverageNet):
    """
    A `CoverPoint` is designed to track when a single particular event occurs.
    """
    from ..model import Signal

    def get_type(self) -> str:
        """
        Returns the name of the coverage type.
        """
        return 'CoverPoint'

    def __init__(self, name: str, goal: int=1, bypass: bool=False, target=None, source=None, sink=None, advancer=None, checker=None):
        """
        Create a new `CoverPoint` object.

        ### Parameters
        - `name`: The name of the coverage net
        - `bypass`: Skips this net when trying to meet coverage if set to true
        - `target`: The signal(s) involved in advancing and checking this net's coverage
        - `source`: The signal(s) involved in advancing the net's coverage
        - `sink`:  The signal(s) involved in checking the net's coverage
        - `advancer`: Specify the function to produce the set of values for the source to advance this net's coverage
        - `checker`: Specify the function to return true when this net has been covered according to the sink's value
       
        The `target` can be a single Signal or an iterable number of Signals. It
        is considered the `source` and `sink` (both read and written).

        The `source` acts as inputs that can be written to when to when trying to advance coverage to a
        scenario that would help approach its goal.

        The `sink` acts as the outputs that are read when checking if this net covered.

        When setting the `advancer`, note that it takes the `source` as input and expects to return
        enough values to set each signal in the `source`.

        When setting the `checker`, note that it takes the `sink` as input and expects to return true 
        if covered and false otherwise.
        """
        self._count = 0
        self._goal = goal
        # define a custom function that should return a boolean to define the targeted point
        self._fn_checker = checker
        self._fn_advancer = advancer

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)

        if len(self.get_source_list()) > 1 and self._fn_advancer == None:
            raise Exception('invalid CoverPoint "'+str(name)+'": `advancer` function must be defined when `source` contains more than one signal')
        if len(self.get_sink_list()) > 1 and self._fn_checker == None:
            raise Exception('invalid CoverPoint "'+str(name)+'": `checker` function must be defined when `sink` contains more than one signal')
        pass

    def to_json(self) -> dict:
        data = super().to_json()
        data.update({
            'count': int(self.get_total_points_met()),
            'goal': int(self.get_total_goal_count()),
        })
        return data

    def get_total_goal_count(self) -> int:
        return self._goal

    def _transform(self, item):
        # unpack the list if one was given
        if self._fn_checker == None:
            return item
        if isinstance(item, (list, tuple)) == True:
            return self._fn_checker(*item)
        else:
            return self._fn_checker(item)

    def is_in_sample_space(self, item) -> bool:
        mapped_item = int(self._transform(item))
        return mapped_item >= 0 and mapped_item < 2

    def _map_onto_range(self, item) -> int:
        if self.is_in_sample_space(item) == False:
            return None
        return int(self._transform(item))

    def get_goal(self) -> int:
        return self._goal

    def get_count(self) -> int:
        return self._count

    def get_range(self) -> range:
        return range(0, 2, 1)
    
    def get_partition_count(self) -> int:
        return 1
    
    def get_points_met(self) -> int:
        """
        Returns the number of points that have met their goal.
        """
        return 1 if self._count >= self._goal else 0
    
    def get_total_points_met(self) -> int:
        return self._count

    def check(self, item):
        """
        Returns `True` if the `cond` was satisfied and updates the internal count
        as the coverpoint tries to met or exceed its goal.
        """
        if self.is_in_sample_space(item) == False:
            return False
        cond = bool(self._map_onto_range(item))
        if cond == True:
            self._count += 1
        return cond
    
    def advance(self, rand=False):
        from ..signal import Signal as _Signal
        if self._fn_advancer == None:
            next_value = int(True)
            if isinstance(self._source, _Signal):
                self._source.value = next_value
                return None
            else:
                return next_value
        else:
            if isinstance(self._source, (list, tuple)) == True:
                to_return = []
                result = self._fn_advancer(*self._source)
                if result is None:
                    return None
                for (i, s) in enumerate(self._source):
                    if isinstance(s, _Signal) == True:
                        s.value = result[i]
                        to_return += [None]
                    else:
                        to_return += [result[i]]
                return to_return
            else:
                result = self._fn_advancer(self._source)
                if result is None:
                    return None
                if isinstance(self._source, _Signal) == True:
                    self._source.value = result
                    return None
                else:
                    return result

    def passed(self):
        return self._count >= self._goal

    def to_string(self, verbose: bool):
        return str(self._count) + '/' + str(self._goal)
    
    pass