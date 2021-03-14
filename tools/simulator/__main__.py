""" Simulate system runs """
# pylint: disable=logging-fstring-interpolation

# standard libs
import signal
import logging

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
    signal.signal(signal.SIGINT, simulator.signal_handler)
    simulator.run()

def setup_logger():
    """ Basic logger configuration """
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
