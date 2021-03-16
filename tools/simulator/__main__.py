""" Simulate system runs """
# pylint: disable=logging-fstring-interpolation

# standard libs
import logging
import sys
import os

from .config import setup_argparser
from .simulator import Simulator

BANNER = """
██   ██ ██   ██  ██████  ██    ██ ███    ██ ██████  ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ████   ██ ██   ██ ██   ██ ██ 
  ███   ███████ ██    ██ ██    ██ ██ ██  ██ ██   ██ ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ██  ██ ██ ██   ██ ██      ██ 
██   ██ ██   ██  ██████   ██████  ██   ████ ██████  ██      ██
"""

logger = logging.getLogger()

def main():
    """ Entry point for the simulator """
    print(BANNER)
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    simulator = Simulator(options)
    test_passed = simulator.run_and_test()

    logger.log(level=logging.INFO if test_passed else logging.ERROR,
        msg="Simulation smoke test PASSED" if test_passed
        else "Simulation smoke test FAILED")

    sys.exit(0 if test_passed else 1)

def setup_logger():
    """ Basic logger configuration """
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('SIMULATOR:[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
