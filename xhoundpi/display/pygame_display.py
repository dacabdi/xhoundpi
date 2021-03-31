""" PyGame based display used for fake display rendering """

import asyncio
import numpy
import pygame

from .framebuffer import FrameBuffer

class PyGameDisplay:
    """
    PyGame based display used for fake display rendering
    """

    def __init__(self, frame: FrameBuffer, scale=1):
        # pylint: disable=no-member
        self._height = frame.height * scale
        self._width = frame.width * scale
        self._frame = frame
        pygame.init()
        pygame.display.set_caption('xHoundPi Panel Simulation')
        self._screen = pygame.display.set_mode(
            (self._width, self._height),
            pygame.NOFRAME)
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
            # yield the thread
            await asyncio.sleep(0)

    def render(self, frame):
        """
        Render frame onto screen
        """
        if self._active:
            self._clear()
            self._set_frame(frame)

    def _clear(self):
        self._screen.fill('black')

    def _set_frame(self, frame: numpy.ndarray):
        # Get a numpy array to display from the simulation
        surface = pygame.surfarray.make_surface(frame)
        surface = pygame.transform.scale(surface, (self._width, self._height))
        self._screen.blit(surface, (0, 0))
        pygame.display.flip()

    def __del__(self):
        if self._active:
            self._active = False
            pygame.quit() # pylint: disable=no-member
