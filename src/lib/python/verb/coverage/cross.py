from .net import CoverageNet
from .ranger import CoverRange

class CoverCross(CoverageNet):
    """
    A `CoverCross` is designed to track cross products between two or more coverage nets.

    Internally, a `CoverCross` stores a `CoverRange` for the 1-dimensional flatten version of
    the N-dimensional cross product across the different coverage nets.
    """
    from typing import List as List

    def get_type(self) -> str:
        """
        Returns the name of the coverage type.
        """
        return 'CoverCross'

    def __init__(self, name: str, nets: List[CoverageNet], goal: int=1, bypass: bool=False, max_steps: int=64, target=None, source=None, sink=None, advancer=None, checker=None):
        """
        Create a new `CoverCross` instance.

        ### Parameters
        - `nets`: specify the coverage nets to cross
        - `max_steps`: specify the maximum number of steps to cover the entire range
        """
        self._nets = nets[::-1]
        self._goal = goal
        self._max_steps = max_steps

        self._crosses = len(self._nets)
        
        combinations = 1
        for n in self._nets:
            combinations *= n.get_partition_count()
            pass

        self._inner = CoverRange(
            name=name,
            span=range(combinations),
            goal=self._goal,
            bypass=bypass,
            max_steps=self._max_steps
        )

        sink = []
        net: CoverageNet
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
        # remove the interior range net and only track this outer net
        CoverageNet._group.pop()
        
        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass

    def to_json(self) -> dict:
        data = self._inner.to_json()
        return data

    def get_total_goal_count(self) -> int:
        return self._inner.get_total_goal_count()
    
    def goal(self, goal: int):
        self._goal = goal
        return self
    
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
        # print('----', self._inner.get_partition_count())

        j = self._flatten(item)
        # print(item, '->', j)

        n = self.get_cross_count()

        final = []
        # expand to the entire parition space for each element
        for i, net in enumerate(self._nets):
            # print(net.advance(rand))
            # print(net, net.get_range().step)
            # print(self._nets[n-i-1].get_range().step)
            final += [item[i] * self._nets[n-i-1].get_range().step]

        # print(index, '-->', item, final)
        # exit('implement!')
        return final[::-1]

    def get_range(self) -> range:
        return self._inner.get_range()
    
    def get_partition_count(self) -> int:
        return self._inner.get_partition_count()

    def is_in_sample_space(self, item) -> bool:
        for i, x in enumerate(item):
            if self._nets[i].is_in_sample_space(x) == False:
                return False
        return True
    
    def get_cross_count(self) -> int:
        """
        Returns the number of elements are involved in the cartesian cross product.
        """
        return self._crosses
    
    def _pack(self, index):
        """
        Packs a 1-dimensional index into a N-dimensional item.
        """
        # print('to3D!')
        # initialize the set of values to store in the item
        item = [0] * self.get_cross_count()

        subgroup_sizes = [1] * self.get_cross_count()
        # print(subgroup_sizes)
        for i in range(self.get_cross_count()):
            subgroup_sizes[i] = self._nets[i].get_partition_count()
            # for j in range(i+1, self.get_cross_count()):
            #     subgroup_sizes[i] *= self._nets[i].get_partition_count()
        #     pass
        # print(index)
        subgroup_sizes = subgroup_sizes[::-1]
        #  print('sub', subgroup_sizes)
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
        """
        Flattens an N-dimensional item into a 1-dimensional index.

        Reference: 
        - https://stackoverflow.com/questions/7367770/how-to-flatten-or-index-3d-array-in-1d-array
        """
        # print('to 1d!')
        if len(item) != self.get_cross_count():
            raise Exception("Expects "+str(self._crosses)+" values in pair")
        index = 0
        #  print('3d:', item)
        # dimensions go: x, y, z... so reverse the tuple/list
        weights = [1]
        n = self.get_cross_count()
        for i, d in enumerate(item):
            index += int(d) * weights[-1]
            weights += [weights[-1] * self._nets[n-i-1].get_partition_count()]
            pass
        # print(weights)
        # print('NOW:', index)
        return index

    def _map_onto_range(self, item):
        return self._flatten(item)
    
    def get_points_met(self) -> int:
        """
        Returns the number of points that have met their goal.
        """
        return self._inner.get_points_met()

    def get_goal(self) -> int:
        return self._inner.get_goal()

    def get_count(self) -> int:
        return self._inner.get_count()
    
    def get_total_points_met(self) -> int:
        return self._inner.get_total_points_met()

    def check(self, item):
        if self.is_in_sample_space(item) == False:
            return None
        rev = []
        for i, it in enumerate(item):
            rev += [int(int(it) / self._nets[i].get_range().step)]
        rev = rev[::-1]
        # divide by the steps
        index = self._flatten(rev)
        return self._inner.check(index)

    def passed(self):
        return self._inner.passed()
    
    def to_string(self, verbose: bool):
        return self._inner.to_string(verbose)

    pass
