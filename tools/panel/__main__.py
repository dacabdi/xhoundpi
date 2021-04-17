""" xHoundPi panel system proof of concept """
# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position

# print debugging information
# before loadint anything
import os
import sys
import pprint
pprint.pprint(os.getcwd())
pprint.pprint(sys.path)
pprint.pprint(dict(os.environ), width=1)

# standard libs
import logging
import asyncio

from tools.panel.config import setup_argparser
from tools.panel.panel import Panel

BANNER = """
██   ██ ██   ██  ██████  ██    ██ ███    ██ ██████  ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ████   ██ ██   ██ ██   ██ ██ 
  ███   ███████ ██    ██ ██    ██ ██ ██  ██ ██   ██ ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ██  ██ ██ ██   ██ ██      ██ 
██   ██ ██   ██  ██████   ██████  ██   ████ ██████  ██      ██
 _  _  _  _ |   _  _  _
|_)(_|| |(/_|  |_)(_)(_
|              |
"""

logger = logging.getLogger()

async def main_async():
    """xHoundPi entry point"""
    print(BANNER)
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    await Panel(options).run()

def main():
    """ Entry point and async main scheduler """
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    sys.exit(exit_code)

def setup_logger():
    """ Basic logger configuration """
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('SIMULATOR:[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
