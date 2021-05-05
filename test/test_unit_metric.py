# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import Mock, call
from xhoundpi.metric import (LatencyMetric,
                            CounterMetric,
                            ValueMetric,
                            SuccessCounterMetric,
                            MetricsCollection,)

from test.time_utils import FakeStopWatch

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

        self.assertEqual(metric.mappify(), {'latency1': 20.0})
        self.assertEqual(str(metric), "{'latency1': 20.0}")

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

        self.assertEqual(metric.mappify(), {'latency1': 20.0})

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

        self.assertEqual(metric.mappify(), {'latency1': 20.0})

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
        self.assertEqual(metric.mappify(), {'counter1': 2})
        self.assertEqual(str(metric), "{'counter1': 2}")

class test_ValueMetric(unittest.TestCase): # pylint: disable=invalid-name

    def test_value_add_subtract(self):
        hook = Mock()
        metric = ValueMetric('value1', [hook])
        # NOTE value metrics notify the hook with initial
        # value to ensure priming metric collectors
        hook.assert_called_once_with('value1', 0)
        self.assertEqual(metric.value, 0)
        metric.add(10)
        hook.assert_called_with('value1', 10)
        self.assertEqual(metric.value, 10)
        metric.subtract(3)
        hook.assert_called_with('value1', 7)
        self.assertEqual(metric.value, 7)
        metric.subtract(10)
        hook.assert_called_with('value1', -3)
        self.assertEqual(metric.value, -3)
        metric.add(3)
        hook.assert_called_with('value1', 0)
        self.assertEqual(metric.value, 0)
        self.assertEqual(metric.mappify(), {'value1': 0})
        self.assertEqual(str(metric), "{'value1': 0}")

class test_SuccessCounterMetric(unittest.TestCase): # pylint: disable=invalid-name

    def test_counter(self):
        hook = Mock()
        metric = SuccessCounterMetric('counter1', [hook])

        # NOTE counters notify the hook with initial
        # value to ensure priming metric collectors
        hook.assert_has_calls([call('counter1_success', 0), call('counter1_failure', 0)])
        self.assertEqual(metric.success, 0)
        self.assertEqual(metric.failure, 0)
        self.assertEqual(metric.total, 0)

        metric.increase(is_success=True)
        hook.assert_called_with('counter1_success', 1)
        self.assertEqual(metric.success, 1)
        self.assertEqual(metric.failure, 0)
        self.assertEqual(metric.total, 1)

        metric.increase(is_success=False)
        hook.assert_called_with('counter1_failure', 1)
        self.assertEqual(metric.success, 1)
        self.assertEqual(metric.failure, 1)
        self.assertEqual(metric.total, 2)

        metric.increase(is_success=True)
        hook.assert_called_with('counter1_success', 2)
        self.assertEqual(metric.success, 2)
        self.assertEqual(metric.failure, 1)
        self.assertEqual(metric.total, 3)

        self.assertEqual(metric.mappify(), {
            'counter1_success': 2,
            'counter1_failure': 1,
        })

        self.assertEqual(str(metric), "{'counter1_success': 2, 'counter1_failure': 1}")

class StubMetric:

    def __init__(self, dimension, mapping):
        self._dimension = dimension
        self._mapping = mapping

    @property
    def dimension(self):
        return self._dimension

    def mappify(self):
        return self._mapping

class test_MetricsCollection(unittest.TestCase): # pylint: disable=invalid-name

    def test_metrics_collection(self):
        metric1 = StubMetric('metric1', {'dim1': 0.3, 'dim2': 19.3})
        metric2 = StubMetric('metric2', {'dim3': 0.2, 'dim4': 3.4})
        metric3 = StubMetric('metric3', {'dim5': 20 })

        collection = MetricsCollection([metric1, metric2, metric3])

        # pylint: disable=no-member
        self.assertEqual(collection.metric1, metric1)
        self.assertEqual(collection.metric2, metric2)
        self.assertEqual(collection.metric3, metric3)
        self.assertEqual(collection.mappify(), {
            'dim1': 0.3,
            'dim2': 19.3,
            'dim3': 0.2,
            'dim4': 3.4,
            'dim5': 20
        })
        self.assertEqual(str(collection), "{"
            "'dim1': 0.3, "
            "'dim2': 19.3, "
            "'dim3': 0.2, "
            "'dim4': 3.4, "
            "'dim5': 20"
        "}")

    def test_metrics_collection_empty(self):
        collection = MetricsCollection([])
        self.assertEqual(collection.mappify(), {})
        self.assertEqual(str(collection), '{}')
