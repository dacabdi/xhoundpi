""" Simulate system runs """
# pylint: disable=logging-fstring-interpolation

import argparse
import logging
import os

from tools.capture_processor.parser import parser

BANNER = """
██   ██ ██   ██  ██████  ██    ██ ███    ██ ██████  ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ████   ██ ██   ██ ██   ██ ██ 
  ███   ███████ ██    ██ ██    ██ ██ ██  ██ ██   ██ ██████  ██ 
 ██ ██  ██   ██ ██    ██ ██    ██ ██  ██ ██ ██   ██ ██      ██ 
██   ██ ██   ██  ██████   ██████  ██   ████ ██████  ██      ██
"""

MODULE_CALL = '\
python \
-m xhoundpi \
--mock-gnss \
--gnss-mock-input {gnss_input} \
--gnss-mock-output {gnss_output}'

logger = logging.getLogger()

def main():
    """ Entry point for the simulator """
    print(BANNER)
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    if options.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info('Starting simulator session for xHoundPi!')
    logger.info(f'Configuration options \'{vars(options)}\'')
    logger.debug(f'Exec path \'{os.get_exec_path()}\'')

    options.gnssinput = parse_gnss_input(options)

    cmd = MODULE_CALL.format(
        gnss_input=options.gnssinput,
        gnss_output=options.gnssoutput)
    logger.info(f'Starting xHoundPi with command {cmd}')

    exit_code = os.system(cmd)

    logger.log(logging.INFO if exit_code == 0 else logging.ERROR,
        f'xHoundPi exited with code {exit_code}')

    logger.info('Cleaning up')
    cleanup(options)

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Simulates xHoundPi runs')
    config.add_argument('gnssinput', help='gnss in file')
    config.add_argument('gnssoutput', help='gnss out file')
    config.add_argument('--parse-gnss-input', action='store_true', dest='parse_gnss_input',
        help='gnss-input is ascii capture')
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    return config

def parse_gnss_input(options):
    """ Parse gnss input if needed """
    gnss_input_path = options.gnssinput
    if options.parse_gnss_input:
        logger.info('Parsing capture file for GNSS input')
        gnss_input_path += '.bin'
        with open(options.gnssinput, 'r') as capture,\
             open(gnss_input_path, 'wb') as gnss_input:
            parser(capture, gnss_input)
    logger.info(f'GNSS binary input file path \'{gnss_input_path}\'')
    return gnss_input_path

def cleanup(options):
    """ Clean up after simulation """
    if options.parse_gnss_input:
        logger.info('Deleting parsed binary gnss input file')
        os.remove(options.gnssinput)

def setup_logger():
    """ Basic logger configuration """
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

main()
