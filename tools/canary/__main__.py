''' Simulate system runs '''
# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position,wrong-import-order

# https://patorjk.com/software/taag/#p=display&f=Banner3-D&t=xHoundPi%20Simulator
BANNER = '''

         .-"-.            _____
        / 4 4 \\         / ____|
        \\_ v _/        | |     __ _ _ __   __ _ _ __ _   _
        //   \\         | |    / _` | '_ \\ / _` | '__| | | |
       ((     ))       | |___| (_| | | | | (_| | |  | |_| |
 =======""===""=======  \\_____\\__,_|_| |_|\\__,_|_|   \\__, |
          |||                                         __/ |
          '|'                                        |___/

          xHoundPi's Simulator and Smoke Tester

'''
print(BANNER)
from xhoundpi.diagnostics import describe_environment
print(describe_environment())

import sys
import logging

from .config import setup_argparser
from .canary import Canary

logger = logging.getLogger()

def main():
    ''' Entry point for the simulator '''
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    canary = Canary(options)
    test_passed = canary.run_and_test()

    logger.log(level=logging.INFO if test_passed else logging.ERROR,
        msg="Simulation smoke test PASSED" if test_passed
        else "Simulation smoke test FAILED")

    sys.exit(0 if test_passed else 1)

def setup_logger():
    ''' Basic logger configuration '''
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('CANARY:[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
