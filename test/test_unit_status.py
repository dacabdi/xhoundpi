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

    def test_equality(self):
        status1 = Status(Exception('This parrot is gone to meet its maker'), {'x':3})
        status2 = Status(Exception('This parrot is gone to meet its maker'), {'x':3})
        status3 = Status(Exception('This parrot is gone to meet its maker'), {'x':3})
        status4 = Status(None, {'x':1})

        status_none1 = Status.OK()
        status_none2 = Status.OK()

        # reflexive, symmetric, and transitive
        self.assertEqual(status1, status2)
        self.assertEqual(status2, status1)
        self.assertEqual(status2, status3)
        self.assertEqual(status1, status3)
        self.assertEqual(status1, status1)
        self.assertNotEqual(status1, status4)
        self.assertEqual(status_none1, status_none2)
        self.assertNotEqual(status_none1, status1)

    def test_str(self):
        status1 = Status(Exception('This parrot is gone to meet its maker'), {'x':3})
        status2 = Status(None, {'x':1})
        status3 = Status(None, None)

        self.assertEqual(
            "ok=False, "
            "error=Exception('This parrot is gone to meet its maker'), "
            "metadata={'x': 3}",
            str(status1))

        self.assertEqual(
            "ok=True, "
            "error=None, "
            "metadata={'x': 1}",
            str(status2))

        self.assertEqual(
            "ok=True, "
            "error=None, "
            "metadata={}",
            str(status3))

    def test_repr(self):
        status1 = Status(Exception('This parrot is gone to meet its maker'), {'x':3})
        status2 = Status(None, {'x':1})
        status3 = Status(None, None)

        self.assertEqual(
            "<xhoundpi.status.Status"
            "(ok=False, "
            "error=Exception('This parrot is gone to meet its maker'), "
            "metadata={'x': 3}) "
            f"object at {hex(id(status1))}>",
            repr(status1))

        self.assertEqual(
            "<xhoundpi.status.Status"
            "(ok=True, "
            "error=None, "
            "metadata={'x': 1}) "
            f"object at {hex(id(status2))}>",
            repr(status2))

        self.assertEqual(
            "<xhoundpi.status.Status"
            "(ok=True, "
            "error=None, "
            "metadata={}) "
            f"object at {hex(id(status3))}>",
            repr(status3))
