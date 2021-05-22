''' Bluetooth validation entry point '''
# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position,wrong-import-order

from xhoundpi.diagnostics import describe_environment
print(describe_environment())

# standard libs
import os
import logging
import asyncio
import sys
import csv
import pathlib

from .config import setup_argparser
from .yappy import Yappy

logger = logging.getLogger()

async def main_async():
    '''
    Entry point for the serial validator
    '''
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    logger.info(f'Configuration options: {options}')
    logger.info(f'Current working directory "{os.getcwd()}"')
    logger.info(f'Environment variables "{os.environ}"')

    with open(str(pathlib.Path(__file__).parent.absolute()) + '/' + 'sets.csv') as sets_file:
        sets = list(csv.reader(sets_file))

    sys.exit(await Yappy(options, sets).run())

def main():
    ''' Entry point and async main scheduler '''
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    sys.exit(exit_code)

def setup_logger():
    ''' Basic logger configuration '''
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('YAP:[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
