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
        """
        self._count = 0
        self._goal = goal
        # define a custom function that should return a boolean to define the targeted point
        self._fn_checker = checker
        self._fn_advancer = advancer

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
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
        return 2
    
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
        if self._fn_advancer == None:
            return int(True)
        else:
            if isinstance(self._source, (list, tuple)) == True:
                return self._fn_advancer(*self._source)
            else:
                return self._fn_advancer(self._source)

    def passed(self):
        return self._count >= self._goal

    def to_string(self, verbose: bool):
        return str(self._count) + '/' + str(self._goal)
    
    pass