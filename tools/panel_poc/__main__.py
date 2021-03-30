""" xHoundPi panel system proof of concept """
# pylint: disable=logging-fstring-interpolation

# standard libs
import logging
import sys
import asyncio

from tools.panel_poc.config import setup_argparser
from tools.panel_poc.panel_poc import PanelPoc

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

    await PanelPoc(options).run()

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
