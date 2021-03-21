# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest

from unittest.mock import patch

from xhoundpi.time import StopWatch, TimeError

class test_StopWatch(unittest.TestCase): # pylint: disable=invalid-name

    def test_start_stop(self):
        stopwatch = StopWatch()
        with patch('time.perf_counter', return_value=10.5):
            elapsed_start, start = stopwatch.start()
        with patch('time.perf_counter', return_value=11.5):
            elapsed_stop, stop = stopwatch.stop()
        self.assertEqual(elapsed_start, 0)
        self.assertEqual(start, 10.5)
        self.assertEqual(elapsed_stop, 1.0)
        self.assertEqual(stop, 11.5)

    def test_start_twice_without_stop_should_except(self):
        stopwatch = StopWatch()
        with patch('time.perf_counter', return_value=10.5),\
             self.assertRaises(TimeError) as context:
            elapsed_start, start = stopwatch.start()
            _, _ = stopwatch.start()

        self.assertEqual(elapsed_start, 0)
        self.assertEqual(start, 10.5)
        self.assertEqual(repr(context.exception),
            "TimeError('Stopwatch already started')")

    def test_stop_without_start_should_except(self):
        stopwatch = StopWatch()
        with patch('time.perf_counter', return_value=10.5),\
             self.assertRaises(TimeError) as context:
            _, _ = stopwatch.stop()

        self.assertEqual(repr(context.exception),
            "TimeError('Cannot stop stopwatch before starting')")
