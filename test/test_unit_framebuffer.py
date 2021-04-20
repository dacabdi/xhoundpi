# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
import numpy as np

from xhoundpi.panel.geometry import Geometry
from xhoundpi.panel.framebuffer import FrameBuffer

class test_FrameBuffer(unittest.TestCase):

    def test_framebuffer(self): # pylint: disable=no-self-use
        subscriber = Mock()
        geometry = Geometry(rows=3, cols=5, channels=3, depth=8)
        buff = FrameBuffer(geometry)

        self.assertEqual(buff.geometry, Geometry(rows=3, cols=5, channels=3, depth=8))
        self.assertEqual(buff.frame.all(), np.zeros((3,5,3)).all())
        self.assertEqual(buff.canvas.all(), np.zeros((3,5,3)).all())
        self.assertEqual('uint8', buff.pixel_type)

        buff.subscribe(subscriber)
        buff.canvas[:] = np.full((3,5,3), fill_value=1)
        buff.update()
        self.assertEqual(buff.frame.all(), np.full((3,5,3), fill_value=1).all())
        self.assertEqual(buff.canvas.all(), np.zeros((3,5,3)).all())
        subscriber.assert_called_once_with(buff.frame)

        buff.canvas[:,:] = np.full((3,5,3), fill_value=7)
        buff.update()
        self.assertEqual(buff.frame.all(), np.full((3,5,3), fill_value=7).all())
        self.assertEqual(buff.canvas.all(), np.zeros((3,5,3)).all())
        subscriber.assert_called_with(buff.frame)

    def test_pixel_type(self):
        self.assertEqual('uint8' , (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth= 1))).pixel_type)
        self.assertEqual('uint8' , (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth= 7))).pixel_type)
        self.assertEqual('uint8' , (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth= 8))).pixel_type)
        self.assertEqual('uint16', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth= 9))).pixel_type)
        self.assertEqual('uint16', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=15))).pixel_type)
        self.assertEqual('uint16', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=16))).pixel_type)
        self.assertEqual('uint32', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=17))).pixel_type)
        self.assertEqual('uint32', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=31))).pixel_type)
        self.assertEqual('uint32', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=32))).pixel_type)
        self.assertEqual('uint64', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=33))).pixel_type)
        self.assertEqual('uint64', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=63))).pixel_type)
        self.assertEqual('uint64', (FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=64))).pixel_type)

    def test_pixel_type_unsupported(self):
        with self.assertRaises(ValueError):
            FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=-1))
        with self.assertRaises(ValueError):
            FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=0))
        with self.assertRaises(ValueError) as context:
            FrameBuffer(Geometry(rows=3, cols=5, channels=3, depth=65))
        self.assertEqual('Pixel depth value 65 not supported. '
                'Supported values range from 1 to 64 bits.', str(context.exception))
