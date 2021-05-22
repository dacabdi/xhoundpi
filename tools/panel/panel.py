''' xHoundPi Panel POC module '''
# pylint: disable=logging-fstring-interpolation

import logging
import signal
import sys
import os
import asyncio

import numpy as np
from PIL import Image, ImageFont

from xhoundpi.config import display_mode
from xhoundpi.panel.util import copyto_withpos
from xhoundpi.panel.geometry import Geometry
from xhoundpi.panel.fakepanel import GifDisplay, PyGameDisplay
from xhoundpi.panel.framebuffer import FrameBuffer

logger = logging.getLogger()

class Panel():
    ''' xHoundPi Panel POC context handlers '''

    # pylint: disable=too-many-instance-attributes
    def __init__(self, options):
        self._options = options
        self._tasks = []
        self._tasks_gather = None
        self._setup_signals()
        self._mode = display_mode(options.mode)
        self._geometry = Geometry(
            rows=options.display_height,
            cols=options.display_width,
            channels=self._mode.channels,
            depth=self._mode.depth)
        self._frame = FrameBuffer(self._geometry)
        self._setup_display()

    def _setup_signals(self):
        ''' Subscribe to signals '''
        self._signal = None
        self._signal_frame = None
        signal.signal(signal.SIGINT, self._signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self._signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_display(self):
        driver = self._options.driver
        if driver == 'pygame':
            self._display = PyGameDisplay(self._frame, scale=self._options.scale)
            self._tasks.append(self._display.mainloop())
        elif driver  == 'gif':
            self._display = GifDisplay(self._mode, self._frame)
        else:
            raise NotImplementedError(
                "Currently only 'gif' and 'pygame'"
                "display modes are supported")

    async def run(self):
        ''' Run display POC '''
        self._pre_run()
        self._tasks.append(self._update_frame_loop())
        self._tasks_gather = asyncio.gather(*self._tasks)
        try:
            await self._tasks_gather
        except asyncio.exceptions.CancelledError:
            if self._signal and self._signal_frame:
                signal_name = str(signal.Signals(self._signal)).removeprefix('Signals.') # pylint: disable=no-member
                logger.warning(f'Received signal \'{signal_name}\', exiting now')
                return 0
            logger.exception('Running tasks unexpectedly cancelled')
            return 1
        finally:
            self._post_run()

    def _pre_run(self):
        ''' Prepare to run '''
        if self._options.verbose:
            logger.setLevel(logging.DEBUG)
        logger.info('Starting Pannel POC session for xHoundPi!')
        logger.debug(f'Configuration options: {self._options}')
        logger.debug(f'Current working directory "{os.getcwd()}"')
        logger.debug(f'Environment variables "{os.environ}"')

    def _post_run(self):
        pass

    def _signal_handler(self, sig, frame): # pylint: disable=unused-argument
        ''' Signals handler '''
        # pylint: disable=attribute-defined-outside-init
        self._signal = sig
        self._signal_frame = frame
        if self._tasks_gather:
            self._tasks_gather.cancel()

    async def _update_frame_loop(self):
        while True:
            px_type = self._frame.pixel_type
            np.copyto(
                self._frame.canvas,
                np.random.randint(
                    low=np.iinfo(px_type).min,
                    high=2 ** self._geometry.depth, #np.iinfo(px_type).max,
                    size=self._geometry.shape(),
                    dtype=self._frame.pixel_type))
            copyto_withpos(self._frame.canvas, self._make_text(), (8,8))
            self._frame.update()
            await asyncio.sleep(1/60)

    def _make_text(self):
        img = Image.new(self._mode.pilmode, (64, 48), color='black')
        img_w, img_h = img.size
        font = ImageFont.truetype('fonts/clacon.ttf', 18)
        mask = font.getmask('text', mode=self._mode.pilmode)
        mask_w, mask_h = mask.size
        draw = Image.core.draw(img.im, 0)
        draw.draw_bitmap(((img_w - mask_w)/2, (img_h - mask_h)/2), mask, 2 ** self._mode.depth - 1)
        return np.array(img)
