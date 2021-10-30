''' Human input POC '''

import logging
import asyncio
import signal
import sys

from datetime import datetime

from xhoundpi.event_bus import Event, EventTopic
from xhoundpi.panel.keyboard import KeyboardListener

# pylint: disable=logging-format-interpolation
logger = logging.getLogger()

class HumanInputPynput:

    def __init__(self, options):
        self._options = options
        self._register_signals()
        self._running = False
        self._eventbus = EventTopic('input', datetime.now)
        self._keyboard = KeyboardListener(self._eventbus)

    async def run(self):
        '''
        Run the human input scenario PoC
        '''
        self._running = True
        self._eventbus.subscribe(self._on_input)
        self._keyboard.start()
        while self._running:
            # trick to yield
            await asyncio.sleep(0)

    def _on_input(self, event: Event) -> None:
        print("on_input")
        logger.info(event.payload)

    # os signals handling

    def _register_signals(self):
        self._signal = None
        self._signal_frame = None
        for sig in self._get_signals():
            signal.signal(sig, self._signal_handler)

    @classmethod
    def _get_signals(cls):
        sigs = [signal.SIGINT]
        if sys.platform == 'win32':
            sigs.append(signal.SIGBREAK)
        return sigs

    def _signal_handler(self, sig, frame): # pylint: disable=unused-argument,no-self-use
        signal_name = str(signal.Signals(sig)).removeprefix('Signals.') # pylint: disable=no-member
        logger.warning(f'Received termination signal \'{signal_name}\', exiting gracefully')
        self._running = False
