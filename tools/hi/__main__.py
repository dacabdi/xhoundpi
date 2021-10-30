''' Keyboard and input buttons POC driver '''
# pylint: disable=wrong-import-position

import asyncio
import logging
import os
import sys

from xhoundpi.diagnostics import describe_environment
from tools.hi.config import setup_argparser
from tools.hi.human_input import HumanInputPynput

logger = logging.getLogger()
print(describe_environment())

async def main_async():
    '''
    Entry point for the input POC driver
    '''
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    # pylint: disable=logging-fstring-interpolation
    logger.info(f'Configuration options: {options}')
    logger.info(f'Current working directory "{os.getcwd()}"')
    logger.info(f'Environment variables "{os.environ}"')

    await HumanInputPynput(options).run()

    return 0

def main():
    ''' Entry point and async main scheduler '''
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    sys.exit(exit_code)

def setup_logger():
    ''' Basic logger configuration '''
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('HI:[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
