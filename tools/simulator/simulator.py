""" xHoundPi Simulator module """
# pylint: disable=logging-fstring-interpolation

import logging
import signal
import sys
import os
import subprocess
import asyncio
import atexit

from xhoundpi.async_ext import run_sync
from tools.capture_processor.parser import parser

logger = logging.getLogger()

class Simulator():
    """ xHoundPi Simulator context handlers """

    MODULE_CALL = (
        'python '
        '-m xhoundpi '
        '--mock-gnss '
        '--gnss-mock-input {gnss_input} '
        '--gnss-mock-output {gnss_output}')

    def __init__(self, options):
        self.options = options
        self.xhoundpi_proc = None
        self.xhoundpi_exit_code = 0
        signal.signal(signal.SIGINT, self.signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler)
        atexit.register(self.last_cleanups)

    def run_and_test(self):
        """ Run a simulation session, smoke test, and report """
        self.pre_run()
        self.run()
        passed = self.smoke_test()
        self.post_run()
        return passed

    def is_running(self):
        """ Check if simulator process is running already """
        return self.xhoundpi_proc is not None

    def pre_run(self):
        """ Prepare to run """
        if self.is_running():
            raise RuntimeError('Simulator is already running')
        if self.options.verbose:
            logger.setLevel(logging.DEBUG)

        logger.info('Starting simulator session for xHoundPi!')
        logger.debug(f'Configuration options: {self.options}')
        logger.debug(f'Current working directory "{os.getcwd()}"')
        logger.debug(f'Environment variables "{os.environ}"')

        self.parse_gnss_input()

    def run(self):
        """ Run service """
        cmd = Simulator.MODULE_CALL.format(
            gnss_input=self.options.gnssinput,
            gnss_output=self.options.gnssoutput)
        logger.info(f'Starting xHoundPi with \'{cmd}\'')
        self.xhoundpi_proc = subprocess.Popen(cmd.split(' '))

    def post_run(self):
        """ Send SIGINT, wait for process to exit, and cleanup environment """
        logger.info('Stopping subprocesses')
        if self.xhoundpi_proc:
            logger.debug('Sending termination signal')
            self.xhoundpi_proc.send_signal(signal.SIGTERM)
            logger.debug('Waiting for process to exit (with timeout 5 secs)')
            try:
                self.xhoundpi_exit_code = self.xhoundpi_proc.wait(5)
            except subprocess.TimeoutExpired:
                logger.warning('Timed out waiting for process to exit, killing it')
                self.xhoundpi_proc.terminate()
            finally:
                self.xhoundpi_proc = None
                logger.log(logging.INFO if self.xhoundpi_exit_code == 0 else logging.WARNING,
                    f'xHoundPi exited with code {self.xhoundpi_exit_code}')
        else:
            logger.warning('Subprocess is not runnig')
        logger.info('Cleaning up')
        self.cleanup()

    def cleanup(self):
        """ Clean up after simulation """
        try:
            if self.options.parse_gnss_input and not self.options.preserve_parsed_input:
                logger.info('Deleting parsed binary GNSS input file')
                if os.path.exists(self.options.gnssinput):
                    os.remove(self.options.gnssinput)
            if not self.options.preserve_output:
                logger.info('Deleting GNSS output file and other simulation artifacts')
                if os.path.exists(self.options.gnssoutput):
                    os.remove(self.options.gnssoutput)
        except Exception: #pylint: disable=broad-except
            logger.exception('An exception ocurred while cleaning up')

    def smoke_test(self):
        """ Check basic main functionality """
        passed = False
        try:
            passed = run_sync(self.test(), self.options.test_timeout)
        except asyncio.exceptions.TimeoutError:
            logger.error("Smoke test time out")
        return passed

    async def test(self):
        """ Smoke test input/output """
        # NOTE this test will evolve as functionalities are added
        logger.info(f'Running smoke test. Timeout set to {self.options.test_timeout} sec(s).')
        try:
            while not os.path.exists(self.options.gnssoutput) \
                  or not os.path.exists(self.options.gnssinput):
                logger.debug(f'Waiting for {self.options.gnssoutput} and '
                    f'{self.options.gnssinput} files to be created')
                await asyncio.sleep(0.5)
            with open(self.options.gnssoutput, 'br') as gnssoutput,\
                open(self.options.gnssinput, 'br') as gnssinput:
                expected = gnssinput.read()
                expected_size = len(expected)
                logger.info(f'Expected output size is {expected_size} bytes')
                unmatched = True
                while unmatched:
                    current = gnssoutput.read()
                    if current.startswith(expected):
                        logger.info('Test succeeded to match output.')
                        return True
                    if len(current) >= expected_size:
                        logger.error('Test failed to match output before surpassing expected size.')
                        return False
                    logger.debug(f'Output length ({len(current)} bytes) below expected '
                        f'size ({expected_size} bytes).')
                    if self.xhoundpi_proc.poll():
                        logger.error('Test failed, subprocess exited early.')
                        return False
                    await asyncio.sleep(1)
        except Exception: #pylint: disable=broad-except
            logger.exception('Failed running smoke test')
            return False

    def parse_gnss_input(self):
        """ Parse GNSS input if needed """
        gnss_input_path = self.options.gnssinput
        if self.options.parse_gnss_input:
            logger.info('Parsing capture file for GNSS input')
            gnss_input_path += '.hex'
            with open(self.options.gnssinput, 'r') as capture,\
                open(gnss_input_path, 'wb') as gnss_input:
                parser(capture, gnss_input)
        logger.info(f'GNSS binary input file path \'{gnss_input_path}\'')
        self.options.gnssinput = gnss_input_path

    def signal_handler(self, sig, frame): # pylint: disable=unused-argument
        """ Signals handler """
        signal_name = str(signal.Signals(sig)).removeprefix('Signals.')
        logger.warning(f'Received termination signal \'{signal_name}\', exiting gracefully')
        self.post_run()
        sys.exit(1)

    def last_cleanups(self):
        """ Last attempt to kill child process """
        logger.debug('Running last resource cleanups before exiting')
        if self.xhoundpi_proc:
            logger.warning('Found zombie child process exiting, killing it as last attempt!')
            os.kill(self.xhoundpi_proc.pid, signal.SIGTERM)
