''' Stopwatch and time management module '''

import time
from typing import Tuple
from abc import ABC, abstractmethod

class TimeError(Exception):
    '''A custom exception used to report time related errors '''

class IStopWatch(ABC):
    ''' Stopwatch contract representation '''

    @abstractmethod
    def start(self) -> Tuple[float, float]:
        ''' Start the stopwatch and return the elapsed period (for
        symmetry with stop) and the start time in fractional seconds '''

    @abstractmethod
    def stop(self) -> Tuple[float, float]:
        ''' Stop the stopwatch and return the elapsed
        period and the stop time in fractional seconds '''

class StopWatch(IStopWatch):
    ''' StopWatch abstraction '''

    def __init__(self):
        self.__start_time = None
        self.__stop_time = None

    def start(self) -> Tuple[float, float]:
        ''' Start the stopwatch and return the elapsed period (for
        symmetry with stop) and the start time in fractional seconds '''
        if self.__start_time is None:
            self.__start_time = time.perf_counter()
            return 0, self.__start_time
        raise TimeError('Stopwatch already started')

    def stop(self) -> Tuple[float, float]:
        ''' Stop the stopwatch and return the elapsed
        period and the stop time in fractional seconds '''
        if self.__start_time is None:
            raise TimeError('Cannot stop stopwatch before starting')
        self.__stop_time = time.perf_counter()
        stop_time = self.__stop_time
        elapsed = self.__stop_time - self.__start_time
        self.__start_time = self.__stop_time = None
        return elapsed, stop_time
