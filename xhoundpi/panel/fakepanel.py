""" Fake panels """

import asyncio
import numpy as np

import pygame
from PIL import Image

from .framebuffer import FrameBuffer

class GifDisplay:
    """
    Gif output display
    """

    def __init__(self, mode, frame: FrameBuffer):
        # pylint: disable=no-member
        self._mode = mode
        self._frame = frame
        self._images = []
        self._active = True
        self._frame.subscribe(self.render)

    def render(self, frame):
        """
        Render frame onto screen
        """
        if self._active:
            self._append_frame(frame)

    def _append_frame(self, frame: np.ndarray):
        image = Image.fromarray(frame, mode=self._mode.pilmode)
        self._images.append(image)
        self._images[0].save('display.gif',
               save_all=True,
               append_images=self._images[1:],
               optimize=True,
               duration=33,
               loop=0)

class PyGameDisplay:
    """
    PyGame based display
    """

    # pylint: disable=no-member
    FLAGS = pygame.NOFRAME | pygame.SHOWN
    TITLE = 'xHoundPi Panel Simulation'

    def __init__(self, frame: FrameBuffer, scale=1):
        # pylint: disable=no-member
        self._geometry = frame.geometry.col_major
        self._frame = frame
        self._scale = scale
        self._init_pygame()
        self._active = True
        self._frame.subscribe(self.render)

    async def mainloop(self):
        """
        PyGame main loop using async programming
        """
        while self._active:
            for event in pygame.event.get():
                # pylint: disable=no-member
                if event.type == pygame.QUIT:
                    self._active = False
            # yield the task
            await asyncio.sleep(0)

    def render(self, frame):
        """
        Render frame onto screen
        """
        if self._active:
            self._clear()
            self._set_frame(frame)

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.TITLE)
        self._screen = pygame.display.set_mode(
            self._size(),
            flags=self.FLAGS)

    def _clear(self):
        self._screen.fill('black')

    def _set_frame(self, frame: np.ndarray):
        # NOTE read calls backwards
        surface = (self.
            _create_surface(self.
            _add_rgb_dimensions(self.
            _scale_values(self.
            _transpose_frame(frame)))))
        self._screen.blit(surface, (0, 0))
        pygame.display.update()

    def _size(self):
        col_major = self._frame.geometry.col_major
        return (col_major[0] * self._scale, col_major[1] * self._scale)

    @classmethod
    def _transpose_frame(cls, frame: np.ndarray) -> np.ndarray:
        # NOTE numpy is row major and pygame is
        # col major, so transposing the
        # first two axes is needed for the dimensions
        # to match
        axes = tuple(range(frame.ndim))
        rearranged = (axes[1], axes[0],) + (axes[2:] if len(axes) > 2 else ())
        return frame.transpose(rearranged)

    def _scale_values(self, frame: np.ndarray) -> np.ndarray:
        # NOTE we support 3 modes
        #    1-bit image b/w
        #    8-bit grayscale
        #   24-bit RGB
        # which should be enough to simulate
        # the spectrum of small hardware displays.
        #
        # However, pygame is not able to provide this level
        # of specifity, we will scale all frames read from
        # the buffer to 24-bit RGB.
        depth = self._frame.geometry.depth
        high = 2 ** depth - 1
        scale = lambda v: (v / high) * 255
        return (scale(frame)).astype(np.uint8)

    @classmethod
    def _add_rgb_dimensions(cls, frame: np.ndarray) -> np.ndarray:
        # TODO this is horrible, find a more efficient/idiomatic
        # way of extending the 2d array into 3d array with repeated values
        if len(frame.shape) < 3:
            new_frame = np.zeros((frame.shape) + (3,), dtype=frame.dtype)
            # pylint: disable=consider-using-enumerate
            for i in range(len(new_frame)):
                for j in range(len(new_frame[i])):
                    new_frame[i][j] = np.array([frame[i][j]])
            return new_frame
        return frame

    def _create_surface(self, frame: np.ndarray):
        return pygame.transform.scale(
            pygame.surfarray.make_surface(frame),
            self._size())

    def __del__(self):
        if self._active:
            self._active = False
            pygame.quit() # pylint: disable=no-member
