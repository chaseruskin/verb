from abc import ABC as _ABC
from enum import Enum as _Enum


class Status(_Enum):
    PASSED = 0
    SKIPPED = 1
    FAILED = 2

    def to_json(self):
        if self == Status.PASSED:
            return True
        elif self == Status.FAILED:
            return False
        elif self == Status.SKIPPED:
            return None
    pass