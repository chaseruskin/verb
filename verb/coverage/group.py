from .net import CoverageNet

class CoverGroup(CoverageNet):
    """
    A `CoverGroup` is designed to track when an instance among multiple different (but somehow related)
    events occur.
    """
    from typing import List as _List
    from ..model import Signal

    def get_type(self) -> str:
        """
        Returns the name of the coverage type.
        """
        return 'CoverGroup'

    def __init__(self, name: str, bins: _List, goal: int=1, bypass: bool=False, max_bins: int=64, target=None, source=None, sink=None, advancer=None, checker=None):
        """
        Create a new `CoverGroup` instance.

        ### Parameters
        - `bins`: specify the explicit grouping of bins
        - `max_bins`: set the maximum number of bins
        """
        # stores the items per index for each bin group
        self._macro_bins = []
        # stores the count for each bin
        self._macro_bins_count = []
        # store a hash to the index in the set of bins list
        self._bins_lookup = dict()

        # store the counts of individual items
        self._item_counts = dict()

        # defining a bin range is more flexible for defining a large space

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()
        self._max_bins = max_bins
        self._goal = goal

        self._bins = bins

        # initialize the total count of all covers
        self._total_count = 0

        # store the function to map items into the coverage space
        self._fn_cover = checker
        # store the function to generate the proper values to advance coverage
        self._fn_advance = advancer

        # will need to provide a division operation step before inserting into
        if len(self._bins) > self._max_bins:
            self._items_per_bin = int(len(self._bins) / self._max_bins)
        else:
            self._items_per_bin = 1

        # initialize the bins
        for i, item in enumerate(set(self._bins)):
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

        super().__init__(name=name, bypass=bypass, target=target, source=source, sink=sink)
        pass

    def to_json(self) -> dict:
        data = super().to_json()
        bins_reached = 0
        # compute the number of bins that reached their goal
        for c in self._macro_bins_count:
            if c >= self._goal:
                bins_reached += 1
            pass
        more_data = {
            'count': int(self.get_points_met()),
            'goal': int(self.get_total_goal_count()),
        }

        bins = []
        for i, macro in enumerate(self._macro_bins):
            cur_bin = {
                'name': self._macro_to_string(i),
                'met': None if self._bypass == True else int(self._macro_bins_count[i]) >= int(self._goal),
                'count': int(self._macro_bins_count[i]),
                'goal': int(self._goal),
            }
            hits = []
            for hit in macro:
                if hit in self._item_counts.keys():
                    hit = {
                        'value': str(hit),
                        'count': int(self._item_counts[hit])
                    }
                    hits += [hit]
                pass
            cur_bin['hits'] = hits
            bins += [cur_bin]
            pass

        more_data['bins'] = bins
        data.update(more_data)
        return data

    def get_total_goal_count(self) -> int:
        return self._goal * len(self._macro_bins_count)
    
    def max_bins(self, limit: int):
        """
        Sets the maximum number of bins.
        """
        self._max_bins = limit
        return self
    
    def bins(self, bins):
        """
        Defines the explicit grouping of bins.
        """
        self._bins = bins
        return self

    def get_goal(self) -> int:
        return self._goal * len(self._macro_bins_count)

    def get_count(self) -> int:
        points_met = 0
        for count in self._macro_bins_count:
            if count >= self._goal:
                points_met += 1
        return points_met

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
        """
        Returns the macro index for the `item` according to the bin division.
        """
        return int(self._bins_lookup[item] / self._items_per_bin)
    
    def check(self, item):
        """
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        """
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
        # track individual count for this item
        if mapped_item not in self._item_counts.keys():
            self._item_counts[mapped_item] = 0
        self._item_counts[mapped_item] += 1

        return is_progress
    
    def get_total_points_met(self) -> int:
        points_met = 0
        for count in self._macro_bins_count:
            points_met += count
        return points_met
    
    def get_points_met(self) -> int:
        points_met = 0
        for count in self._macro_bins_count:
            if count >= self._goal:
                points_met += 1
        return points_met
    
    def advance(self, rand=False):
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
        
        next_value = None
        if rand == True:
            # pick a random macro bin
            i_macro = _random.choice(available)
            # select a random item from the bin
            next_value = _random.choice(self._macro_bins[i_macro])
        else:
            # provide 1st available if random is disabled
            i_macro = available[0]
            next_value = self._macro_bins[i_macro][0]
            
        # assign the next value for the single source
        if isinstance(self._source, _Signal):
            self._source.value = next_value
        else:
            return next_value

    def passed(self) -> bool:
        """
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        """
        for val in self._macro_bins_count:
            # fail on first failure
            if val < self._goal:
                return False
        return True
    
    def _macro_to_string(self, i) -> str:
        """
        Write a macro_bin as a string.
        """
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
        from . import _find_longest_str_len
        result = ''
        # print each individual bin and its goal status
        if verbose == True:
            # determine the string formatting by identifying longest string
            longest_len = _find_longest_str_len([self._macro_to_string(i) for i, _ in enumerate(self._macro_bins)])
            is_first = True
            # print the coverage analysis
            for i, _ in enumerate(self._macro_bins):
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
                    for j, (key, val) in enumerate(seq):
                        result += '\n        '
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