""" Display buffers module """

from typing import Callable
import numpy as np

class FrameBuffer:
    """
    Display pixel frame abstraction
    """

    def __init__(self, height: int, width: int):
        self._height = height
        self._width = width
        self._current_frame = np.zeros((width, height))
        self._next_frame = np.zeros((width, height))
        self._subscribers = []

    def update(self):
        """
        Update current frame with next frame used as canvas
        """
        self._current_frame = self._next_frame
        self._next_frame = np.zeros((self._width, self._height))
        self._notify()

    def subscribe(self, on_update: Callable):
        """
        Subscribe to frame updates
        """
        return self._subscribers.append(on_update)

    @property
    def width(self):
        """
        Get width
        """
        return self._width

    @property
    def height(self):
        """
        Get height
        """
        return self._height

    @property
    def frame(self):
        """
        Currently active frame
        """
        return self._current_frame

    @property
    def canvas(self):
        """
        Next frame to be set on update
        """
        return self._next_frame

    def _notify(self):
        for subscriber in self._subscribers:
            subscriber(self.frame)
