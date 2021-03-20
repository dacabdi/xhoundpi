# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest

from xhoundpi.status import Status

class test_Status(unittest.TestCase):

    def test_ok_factory(self):
        self.assertEqual(Status.OK(), Status(None))
        self.assertEqual(Status.OK({'x':1}), Status(None, {'x':1}))

    def test_error(self):
        status = Status(Exception('houston we have a problem'), metadata={'x':1})
        self.assertFalse(status.ok)
        self.assertIsInstance(status.error, Exception)
        self.assertEqual(str(status.error), 'houston we have a problem')
        self.assertEqual(status.metadata, {'x':1})

    def test_ok_default(self):
        status = Status(None)
        self.assertTrue(status.ok)
        self.assertEqual(status.error, None)
        self.assertEqual(status.metadata, {})

    def test_ok_with_metadata(self):
        status = Status(None, {'x':1})
        self.assertTrue(status.ok)
        self.assertEqual(status.error, None)
        self.assertEqual(status.metadata, {'x':1})
