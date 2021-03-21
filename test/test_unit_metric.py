# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import Mock, call
from xhoundpi.metric import (LatencyMetric,
                            CounterMetric,
                            SuccessCounterMetric)

from .time_utils import FakeStopWatch

class test_LatencyMetric(unittest.TestCase): # pylint: disable=invalid-name

    def test_latency(self):
        stopwatch = FakeStopWatch()
        hook = Mock()
        metric = LatencyMetric('latency1', stopwatch, [hook])

        metric.start()
        self.assertEqual(metric.value, float('inf'))
        stopwatch.elapsed = 10.0
        metric.stop()

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 10.0)
        hook.assert_called_once_with('latency1', 10.0)

        metric.start()
        self.assertEqual(metric.value, float('inf'))
        stopwatch.elapsed = 20.0
        metric.stop()

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 20.0)
        hook.assert_called_with('latency1', 20.0)

    def test_latency_as_context_manager(self):
        stopwatch = FakeStopWatch()
        hook = Mock()
        metric = LatencyMetric('latency1', stopwatch, [hook])

        self.assertEqual(metric.value, float('inf'))

        with metric:
            self.assertEqual(metric.value, float('inf'))
            stopwatch.elapsed = 10.0

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 10.0)
        hook.assert_called_once_with('latency1', 10.0)

        with metric:
            self.assertEqual(metric.value, float('inf'))
            stopwatch.elapsed = 20.0

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 20.0)
        hook.assert_called_with('latency1', 20.0)

    def test_latency_as_context_manager_bubbles_exception(self):
        stopwatch = FakeStopWatch()
        hook = Mock()
        metric = LatencyMetric('latency1', stopwatch, [hook])

        self.assertEqual(metric.value, float('inf'))

        with metric:
            self.assertEqual(metric.value, float('inf'))
            stopwatch.elapsed = 10.0

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 10.0)
        hook.assert_called_once_with('latency1', 10.0)

        with metric:
            self.assertEqual(metric.value, float('inf'))
            stopwatch.elapsed = 20.0

        self.assertEqual(metric.dimension, 'latency1')
        self.assertEqual(metric.value, 20.0)
        hook.assert_called_with('latency1', 20.0)

class test_CounterMetric(unittest.TestCase): # pylint: disable=invalid-name

    def test_counter(self):
        hook = Mock()
        metric = CounterMetric('counter1', [hook])
        # NOTE counters notify the hook with initial
        # value to ensure priming metric collectors
        hook.assert_called_once_with('counter1', 0)
        self.assertEqual(metric.value, 0)
        metric.increase()
        hook.assert_called_with('counter1', 1)
        self.assertEqual(metric.value, 1)
        metric.increase()
        hook.assert_called_with('counter1', 2)
        self.assertEqual(metric.value, 2)

class test_SuccessCounterMetric(unittest.TestCase): # pylint: disable=invalid-name

    def test_counter(self):
        hook = Mock()
        metric = SuccessCounterMetric('counter1', [hook])

        # NOTE counters notify the hook with initial
        # value to ensure priming metric collectors
        hook.assert_has_calls([call('counter1_Success', 0), call('counter1_Failure', 0)])
        self.assertEqual(metric.success, 0)
        self.assertEqual(metric.failure, 0)
        self.assertEqual(metric.total, 0)

        metric.increase(is_success=True)
        hook.assert_called_with('counter1_Success', 1)
        self.assertEqual(metric.success, 1)
        self.assertEqual(metric.failure, 0)
        self.assertEqual(metric.total, 1)

        metric.increase(is_success=False)
        hook.assert_called_with('counter1_Failure', 1)
        self.assertEqual(metric.success, 1)
        self.assertEqual(metric.failure, 1)
        self.assertEqual(metric.total, 2)

        metric.increase(is_success=True)
        hook.assert_called_with('counter1_Success', 2)
        self.assertEqual(metric.success, 2)
        self.assertEqual(metric.failure, 1)
        self.assertEqual(metric.total, 3)
