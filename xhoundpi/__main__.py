"""xHoundPi firmware execution module"""

# standard libs
import asyncio
import logging
import logging.config
import os
import sys

# external imports
import yaml
import structlog

# local imports
from .config import setup_configparser
from .xhoundpi import XHoundPi
from .bound_logger_event import BoundLoggerEvents
from .events import AppEvent

logger = structlog.get_logger('xhoundpi')

async def main_async():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    # setup loggers
    setup_logging(config.log_config_file)
    logger.info(AppEvent(str), config=vars(config))

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
