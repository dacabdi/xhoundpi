""" Simulator configuration parser module """

import argparse

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Simulates xHoundPi runs')
    config.add_argument('gnssinput', help='gnss in file')
    config.add_argument('gnssoutput', help='gnss out file')
    config.add_argument('--parse-gnss-input', action='store_true', dest='parse_gnss_input',
        help='gnss-input is ascii capture')
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    config.add_argument('--preserve-parsed-input', action='store_true',
        dest='preserve_parsed_input', help="skip deleting parsed capture")
    config.add_argument('--preserve-output', action='store_true',
        dest='preserve_output', help="skip output files cleanup")
    config.add_argument('--test-timeout', metavar='SECONDS', dest='test_timeout', type=int,
        default=5, help='time to wait for smoke test to succeed (in secs)')
    return config
