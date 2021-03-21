""" Metrics abstractions module """

import collections
from typing import Any, Callable, Iterable, List, Mapping

from .time import IStopWatch

class MetricBase:
    """ Metrics base class """

    def __init__(self, dimension: str, hooks = List[Callable]):
        self._value = None
        self.__dimension = dimension
        self.__hooks = hooks

    @property
    def dimension(self) -> str:
        """ Get dimension tag """
        return self.__dimension

    @property
    def value(self) -> Any:
        """ Get metric value """
        return self._value

    def _call_hooks(self):
        if isinstance(self.value, collections.Mapping):
            self._call_hooks_multidim(self.value)
            return
        self._call_hooks_single_dim(self.dimension, self.value)

    def _call_hooks_single_dim(self, dimension: str, value: Any):
        for hook in self.__hooks:
            hook(dimension, value)

    def _call_hooks_multidim(self, mapping: Mapping):
        for key, value in mapping.items():
            self._call_hooks_single_dim(key, value)

class LatencyMetric(MetricBase):
    """ Operation latency metric with context manager semantics """

    def __init__(self, dimension: str, stopwatch: IStopWatch, hooks = List[Callable]):
        super().__init__(dimension, hooks)
        self.__stopwatch = stopwatch
        self._value = float('inf')

    def start(self):
        """ Start timer """
        self._value = float('inf')
        self.__stopwatch.start()

    def stop(self):
        """ Stop timer """
        self._value, _ = self.__stopwatch.stop()
        self._call_hooks()

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()
        return exc_info is None

class CounterMetric(MetricBase):
    """ Operation counter metric """

    def __init__(self, dimension: str, hooks = List[Callable]):
        super().__init__(dimension, hooks)
        self._value = 0
        self._call_hooks()

    def increase(self):
        """ Increase internal counter value """
        self._value += 1
        self._call_hooks()
        return self.value

class ValueMetric(MetricBase):
    """ Value based metric """

    def __init__(self, dimension: str, hooks = List[Callable]):
        super().__init__(dimension, hooks)
        self._value = 0
        self._call_hooks()

    def add(self, value):
        """ Add to internal value """
        self._value += value
        self._call_hooks()
        return self.value

    def subtract(self, value):
        """ Substract from internal value """
        self._value -= value
        self._call_hooks()
        return self.value

class SuccessCounterMetric(MetricBase):
    """ Success/failure operation counter metric """

    SUCCESS_SUFFIX='Success'
    FAILURE_SUFFIX='Failure'

    def __init__(self, dimension: str, hooks = List[Callable]):
        super().__init__(dimension, hooks)
        self._value = {
            self._compose_dimension(is_success=True): 0,
            self._compose_dimension(is_success=False): 0,
        }
        self._call_hooks()

    def increase(self, is_success: bool):
        """ Increase internal counter value for success/failure """
        self._increase(is_success=is_success)
        return self.value

    @property
    def success(self):
        """ Report success counter """
        return self._value[self._compose_dimension(is_success=True)]

    @property
    def failure(self):
        """ Report failure counter """
        return self._value[self._compose_dimension(is_success=False)]

    @property
    def total(self):
        """ Report total counter """
        return self.success + self.failure

    def _compose_dimension(self, is_success: bool):
        suffix = self.__class__.SUCCESS_SUFFIX if is_success else self.__class__.FAILURE_SUFFIX
        return f'{self.dimension}_{suffix}'

    def _increase(self, is_success: bool):
        dimension = self._compose_dimension(is_success)
        self._value[dimension] += 1
        self._call_hooks_single_dim(dimension, self._value[dimension])
        return self.value
