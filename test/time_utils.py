# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

from typing import Tuple
from xhoundpi.time import IStopWatch

class FakeStopWatch(IStopWatch):
    """ Fake stopwatch for time related testing """

    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed = None

    def start(self) -> Tuple[float, float]:
        return 0, self.start_time

    def stop(self) -> Tuple[float, float]:
        return self.elapsed, self.stop_time
