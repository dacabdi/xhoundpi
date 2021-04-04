""" Display buffers module """

from typing import Callable, Type

import numpy as np

from .geometry import Geometry

class FrameBuffer:
    """
    Display pixel frame abstraction

    NOTE beware that most display representations
    are column major (the dimensions start with the cols,
    not the rows), however, to be more in accord with
    numpy, we are using row major, thus, transposing
    the image might be neccesary before displaying.
    """

    ORDER = 'C' # numpy's row major

    def __init__(self, geometry: Geometry):
        self._geometry = geometry
        self._pixel_type = self._select_pixel_type(geometry.depth)
        self._current_frame = self._create_frame()
        self._next_frame = self._create_frame()
        self._subscribers = []

    def update(self):
        """
        Update current frame with next frame used as canvas
        """
        temp = self._current_frame
        self._current_frame = self._next_frame
        self._next_frame = temp
        self._next_frame *= 0
        self._notify()

    def subscribe(self, on_update: Callable):
        """
        Subscribe to frame updates
        """
        return self._subscribers.append(on_update)

    @property
    def geometry(self) -> Geometry:
        """
        Frame's geometry
        """
        return self._geometry

    @property
    def frame(self) -> np.ndarray:
        """
        Currently active frame
        """
        return self._current_frame

    @property
    def canvas(self) -> np.ndarray:
        """
        Next frame to be set on update, use as drawing space
        """
        return self._next_frame

    @property
    def pixel_type(self):
        """
        Return numeric type used to
        represent a pixel value per channel
        """
        return self._pixel_type

    def _notify(self):
        for subscriber in self._subscribers:
            subscriber(self.frame)

    def _create_frame(self) -> np.ndarray:
        return np.zeros(
            shape=self.geometry.shape(),
            dtype=self.pixel_type,
            order=self.ORDER)

    def _select_pixel_type(self, depth: int) -> Type:
        if (self._geometry.depth <= 0 or
            self._geometry.depth > 64):
            raise ValueError(
                f'Pixel depth value {depth} not supported. '
                'Supported values range from 1 to 64 bits.')
        if self._geometry.depth <= 8:
            return 'uint8'
        if depth <= 16:
            return 'uint16'
        if depth <= 32:
            return 'uint32'
        return 'uint64'
