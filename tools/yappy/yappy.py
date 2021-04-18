""" xHoundPi Yap bluetooth tester """
# pylint: disable=logging-fstring-interpolation

import asyncio
import logging
import signal
import sys
import random
import string
import json
from datetime import datetime
from io import StringIO

import humanize
import serial
from serial.serialutil import SerialTimeoutException

from xhoundpi.serial import StubSerialBinary, StubSerialText
from xhoundpi.time import StopWatch

logger = logging.getLogger()

class Yappy:
    """
    Yappy context handlers (integration layer)
    """
    READ_TIMEOUT_SEC  = 1
    WRITE_TIMEOUT_SEC = 1

    def __init__(self, options, sets):
        self._options = options
        self._register_signals()
        self._running = None
        self._sets = sets

    async def run(self):
        """
        Run Yappy tests
        """
        a = StringIO()
        b = StringIO()

        logger.info(f"Opening serial A: '{self._options.serial_a}'")
        serial_a = StubSerialText(a, b) #self._open_serial(self._options.serial_a)

        logger.info(f"Opening serial B: '{self._options.serial_b}'")
        serial_b = StubSerialText(b, a)  #self._open_serial(self._options.serial_b)

        try:
            logger.info('Creating and starting test session')
            test_coro = Test(serial_a, serial_b, self._sets).test()
            self._running = asyncio.create_task(test_coro)
            result = await self._running
        except asyncio.exceptions.CancelledError:
            if self._signal and self._signal_frame:
                signal_name = str(signal.Signals(self._signal)).removeprefix('Signals.') # pylint: disable=no-member
                logger.warning(f'Received signal \'{signal_name}\', exiting now')
                return 0
            logger.exception('Running tasks unexpectedly cancelled')
            return 1
        finally:
            self._running = None

        with open('serial_benchmark_results.json', 'w') as fp:
            json.dump(result, fp, indent=4, sort_keys=True, default=str)

        # TODO print out results
        return 0 if result and result['passed'] else 1

    def _open_serial(self, port: str):
        return serial.Serial(
            port=port,
            baudrate=self._options.baudrate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS,
            timeout=self.READ_TIMEOUT_SEC,
            write_timeout=self.WRITE_TIMEOUT_SEC)

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
        """ Signals handler """
        signal_name = str(signal.Signals(sig)).removeprefix('Signals.') # pylint: disable=no-member
        logger.warning(f'Received termination signal \'{signal_name}\', exiting gracefully')
        self._running.cancel()

class Test:
    """
    Yap BT test
    """

    def __init__(self, dev_a, dev_b, sets):
        self._dev_a = dev_a
        self._dev_b = dev_b
        self._sets = sets
        self._result = {
            'started': datetime.now(),
            'finished' : '',
            'sets' : {},
            'passed' : True,
        }

    async def test(self):
        """
        Run a test session and report the results
        """
        await self._run_sets()
        return self._result

    async def _run_sets(self):
        for count, cbytes in self._sets:
            count, cbytes = int(count), int(cbytes)
            key = f'{count} chunks of {humanize.naturalsize(cbytes)}'
            self._result['sets'][key] = await self._run_set(count, cbytes)
        self._result['finished'] = datetime.now()
        return self._result

    async def _run_set(self, chunks, cbytes):
        logger.info(f"Exchanging {chunks} of {humanize.naturalsize(cbytes)}")
        return {
            'from a to b': await self._one_way(chunks, cbytes, self._dev_a, self._dev_b),
            'from b to a': await self._one_way(chunks, cbytes, self._dev_b, self._dev_a),
        }

    async def _one_way(self, chunks, cbytes, tx_ing, rx_ing):
        stopwatch = StopWatch()
        result = {
            'elapsed total': 0,
            'elapsed average per chunk': 0,
            'chunk size': cbytes,
            'chunks count': chunks,
            'chunks result': [],
            'passed': True,
        }
        for _ in range(0, chunks):
            txd = ''
            rxd = ''
            chunk_result = {
                'elapsed': 0,
                'diff': '',
                'passed': True,
                'timeout': None,
            }
            data = self._data(cbytes)

            stopwatch.start()
            try:
                tx_ing.write(data)
                txd = data
                rxd = rx_ing.read(len(data))
            except SerialTimeoutException as ex:
                logger.warning(repr(ex))
                chunk_result['timeout'] = ex
                chunk_result['passed'] = False
            finally:
                elapsed, _ = stopwatch.stop()

            chunk_result['elapsed'] = elapsed
            chunk_result['passed'] = txd == rxd

            result['elapsed total'] += elapsed
            result['chunks result'].append(chunk_result)
            if not chunk_result['passed']:
                result['passed'] = False

        return result

    @classmethod
    def _data(cls, size) -> str:
        return (''.join(random.choice(string.ascii_lowercase)
            for i in range(size)))
