""" xHoundPi Panel POC module """
# pylint: disable=logging-fstring-interpolation

import logging
import signal
import sys
import os
import asyncio

from .fakepanel import FakePanel
from tools.panel_poc.pygame_panel import render

logger = logging.getLogger()

class PanelPoc():
    """ xHoundPi Panel POC context handlers """

    def __init__(self, options):
        self._options = options
        self._tasks = []
        self._tasks_gather = None
        self._setup_signals()
        #self._panel = FakePanel("tools/panel_poc/welcome.bmp")

    def _setup_signals(self):
        """ Subscribe to signals """
        self._signal = None
        self._signal_frame = None
        signal.signal(signal.SIGINT, self._signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self._signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self._signal_handler)

    async def run(self):
        """ Run display POC """
        self._pre_run()
        self._tasks.append(render())
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
        """ Prepare to run """
        if self._options.verbose:
            logger.setLevel(logging.DEBUG)
        logger.info('Starting Pannel POC session for xHoundPi!')
        logger.debug(f'Configuration options: {self._options}')
        logger.debug(f'Current working directory "{os.getcwd()}"')
        logger.debug(f'Environment variables "{os.environ}"')

    def _post_run(self):

        pass

    def _signal_handler(self, sig, frame): # pylint: disable=unused-argument
        """ Signals handler """
        # pylint: disable=attribute-defined-outside-init
        self._signal = sig
        self._signal_frame = frame
        if self._tasks_gather:
            self._tasks_gather.cancel()
