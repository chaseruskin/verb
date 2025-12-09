"""
Classes and methods for setting up functional coverage with coverage nets.
"""

from .cross import CoverCross
from .group import CoverGroup
from .point import CoverPoint
from .ranger import CoverRange

class Coverage:

    _total_coverages = 0
    _passed_coverages = 0
    _point_count = 0
    _total_points = 0

    @staticmethod
    def reset():
        """
        Reset coverage tracking variables.
        """
        from .net import CoverageNet as _CoverageNet
        Coverage._total_coverages = 0
        Coverage._passed_coverages = 0
        Coverage._point_count = 0
        Coverage._total_points = 0
        _CoverageNet.reset()

    @staticmethod
    def get_nets():
        """
        Returns the list of all coverage nets being tracked.
        """
        from .net import CoverageNet as _CoverageNet
        return _CoverageNet._group

    @staticmethod
    def get_failing_nets():
        """
        Returns a list of coverage nets that have not met their coverage goal.

        This function excludes coverage nets that are bypassed.
        """
        from .net import CoverageNet as _CoverageNet
        net: _CoverageNet
        result = []
        for net in _CoverageNet._group:
            # only append nets that are not bypassed and are not completed
            if net.skipped() == False and net.passed() == False:
                result += [net]
            pass
        return result

    @staticmethod
    def report(verbose: bool=True) -> str:
        """
        Compiles a report of the coverage statistics and details. Setting `verbose`
        to `False` will only provide minimal details to serve as a quick summary.
        """
        from .net import CoverageNet as _CoverageNet
        contents = ''
        cov: _CoverageNet
        for cov in _CoverageNet._group:
            contents += cov.log(verbose) + '\n'
        return contents

    @staticmethod
    def count() -> int:
        """
        Returns the number of times the Coverage class has called the 'all_passed'
        function. If 'all_passed' is called once every transaction, then it gives
        a sense of how many test cases were required in order to achieve full
        coverage.
        """
        from .net import CoverageNet as _CoverageNet
        return _CoverageNet._counter
    
    @staticmethod
    def tally_score():
        """
        Iterates through all CoverageNets to compute the ratio of pass/fail.
        """
        from .net import CoverageNet as _CoverageNet
        from .status import Status as _Status

        Coverage._total_coverages = 0
        Coverage._passed_coverages = 0
        Coverage._point_count = 0
        Coverage._total_points = 0
        net: _CoverageNet
        for net in _CoverageNet._group:
            if net.status() == _Status.SKIPPED:
                continue
            Coverage._total_coverages += 1
            Coverage._point_count += net.get_points_met()
            # add up number of points
            Coverage._total_points += net.get_partition_count()
            if net.status() == _Status.PASSED:
                Coverage._passed_coverages += 1
            pass

    @staticmethod
    def percent() -> float:
        """
        Return the percent of all coverages that met their goal. Each covergroup's bin
        is tallied individually instead of tallying the covergroup as a whole.

        Coverages that have a status of `SKIPPED` are not included in the tally.

        Returns `None` if there are no coverages to tally. The percent value is
        from 0.00 to 100.00 percent, with rounding to 2 decimal places.
        """
        Coverage.tally_score()
        passed = Coverage._point_count
        total = Coverage._total_points
        return round((passed/total) * 100.0, 2) if total > 0 else None

    @staticmethod
    def save() -> str:
        """
        Saves the report if not already saved, and then returns the absolute path to the file.
        """
        Coverage.tally_score()
        # write to .json
        # Coverage.to_json('coverage.json')
        # write to report
        Coverage.to_rpt('fcov.rpt')
    
    pass

    @staticmethod
    def get_overall_status():
        from .status import Status as _Status
        if Coverage._total_points == 0:
            return _Status.SKIPPED
        elif Coverage._point_count >= Coverage._total_points:
            return _Status.PASSED
        else:
            return _Status.FAILED

    @staticmethod
    def to_json(path: str):
        """
        Writes the coverage report as a json encoded string.
        """
        import json
        from .. import context
        from .net import CoverageNet as _CoverageNet

        net: _CoverageNet
        report = {
            'seed': context.Context.current()._context._seed,
            'iterations': int(Coverage.count()),
            'score': Coverage.percent(),
            'achieved': Coverage.get_overall_status().to_json(),
            'count': int(Coverage._point_count),
            'points': int(Coverage._total_points),
            'nets': [net.to_json() for net in _CoverageNet._group]
        }

        with open(path, 'w') as fd:
            json.dump(report, fd, indent=4)
        pass

    @staticmethod
    def to_rpt(path: str) -> str:
        """
        Writes the coverage report as a report formatted string.
        """
        import os
        import time
        # write to .txt
        tb_name = 'N/A'
        dut_name = 'N/A'
        # if context.Context.current()._dut != None:
        #     dut_name = str(context.Context.current()._dut)
        # if context.Context.current()._tb != None:
        #     tb_name = str(context.Context.current()._tb)
        header = 'Functional Coverage Report\n'
        header += str(time.strftime("%a %b %d %H:%M:%S %Y")) + '\n'
        # header += 'Verb ' + __version__ + '\n'
        header += '''
+--------------------------------------------+
; Info                                       ;
+--------------------------------------------+
'''
        header += 'Testbench: ' + tb_name + '\n'
        header += 'Module: ' + dut_name+'\n'
        header += "Score: "   + str(Coverage.percent()) + '\n'
        header += "Achieved: " + ('None' if Coverage._total_points == 0 else str(Coverage._point_count >= Coverage._total_points)) + '\n'
        header += "Count: " + str(Coverage._point_count) + '\n'
        header += "Points: " + str(Coverage._total_points) + '\n'
        header += "Iterations: " + str(Coverage.count()) + '\n'
        # header += "Seed: " + str(context.Context.current()._context._seed) + '\n'

        # params = context.Context.current()._parameters
        # if len(params) == 0:
        #     header += "Generics: None\n"
        # else:
        #     header += "Generics:\n"
        #     for p in params:
        #         header += "    " + p['name'] + ": " + str(context.Context.current().generic(p['name'])) + '\n'
        with open(path, 'w') as f:
            # header
            f.write(header) 
            # summary
            f.write('''
+--------------------------------------------+
; Summary                                    ;
+--------------------------------------------+             
''')
            f.write(Coverage.report(False))
            # details
            f.write('''
+--------------------------------------------+
; Details                                    ;
+--------------------------------------------+             
''')
            f.write(Coverage.report(True))
            pass
        return os.path.abspath(path)


def check(threshold: float=1.0) -> bool:
    """
    Determines if coverage was met based on meeting or exceeding the threshold value.

    ### Parameters
    - `threshold` expects a floating point value [0, 1.0]
    """
    Coverage.tally_score()
    passed = Coverage._point_count
    total = Coverage._total_points
    if total <= 0:
        return True
    return float(passed/total) >= threshold


def _find_longest_str_len(x) -> int:
    """
    Given a list `x`, determines the longest length str.
    """
    longest = 0
    for item in x:
        if len(str(item)) > longest:
            longest = len(str(item))
    return longest