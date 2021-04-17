"""xHoundPi firmware execution module"""
# pylint: disable=wrong-import-position

BANNER = '''

                888    888                                 888
                888    888                                 888
                888    888                                 888
       888  888 8888888888  .d88b.  888  888 88888b.   .d88888
       `Y8bd8P' 888    888 d88""88b 888  888 888 "88b d88" 888
         X88K   888    888 888  888 888  888 888  888 888  888
       .d8""8b. 888    888 Y88..88P Y88b 888 888  888 Y88b 888
       888  888 888    888  "Y88P"   "Y88888 888  888  "Y88888

            3,141592653589793238462643383279502884197169399375
        105820974944592307816406286208998628034825342117067982
      14808651328230664709384460955058223172535940812848111745
    0284102701938521105559644622948954930381964428810975665933
    4461284756482337867831652712019091456485669234603486104543
  26648213          393607              26024914
  1273              724587            0066063155
8817                488152            0920962829
25                  409171            53643678
                    925903            60011330
                    530548            82046652
                  138414              69519415
                  116094              33057270
                  365759              59195309
                  218611              73819326
                  117931              05118548
                07446237              99627495
                67351885            7527248912
              2793818301            1949129833
              6733624406            5664308602
            139494639522            4737190702
            1798609437              0277053921              71
          762931767523              8467481846              76
          694051320005              681271452635          6082
        77857713427577              89609173637178      7214
      6844090122495343              014654958537105079227968
      92589235420199                  56112129021960864034
      41815981362977                  47713099605187072113
      499999983729                      7804995105973173
          281609                            63185950

'''
print(BANNER)

from xhoundpi.diagnostics import describe_environment, env_vars
print(describe_environment())

# standard libs
import os
import sys
import pprint
import asyncio
import logging
import logging.config

# external imports
import structlog
import yaml

# local imports
from .config import setup_configparser
from .bound_logger_event import BoundLoggerEvents
from .events import AppEvent
from .xhoundpi import XHoundPi

logger = structlog.get_logger('xhoundpi')

async def main_async():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse() # type: ignore
    parser.print_values()
    pprint.pprint(vars(config))

    # setup loggers
    setup_logging(config.log_config_file)
    logger.info(AppEvent(f"'Configuration loaded': {str(vars(config))}"))
    logger.info(AppEvent(f"'Current working directory': {str(vars(config))}"))
    logger.info(AppEvent(f"'Environment variables: '{env_vars}'"))

    # create and run module
    return await XHoundPi(config).run()

def main():
    """ Entry point and async main scheduler """
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    sys.exit(exit_code)

def setup_logging(config_path):
    """ Setup logging configuration """

    timestamper = structlog.processors.TimeStamper(fmt='iso')
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    # configure logging
    with open(config_path, 'rt') as config_file:
        logger_config = yaml.safe_load(config_file.read())
        # add structlog formatters
        logger_config['formatters'] = {
            "plain": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False, pad_event=0),
                "foreign_pre_chain": pre_chain,
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True, pad_event=0),
                "foreign_pre_chain": pre_chain,
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(indent=1, sort_keys=True),
                "foreign_pre_chain": pre_chain,
            }
        }
        create_log_dirs(logger_config)
        logging.config.dictConfig(logger_config)

    # configure structlog
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=BoundLoggerEvents,
        cache_logger_on_first_use=True)

def create_log_dirs(logger_config):
    """ Check logger configuration for filenames and create subdirs """
    for handler in logger_config['handlers']:
        handler_dict = logger_config['handlers'][handler]
        if 'filename' in handler_dict:
            dirpath = os.path.dirname(handler_dict['filename'])
            os.makedirs(dirpath, exist_ok=True)

main()
