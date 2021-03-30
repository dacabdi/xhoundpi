""" Panel proof of concept configuration parser module """

import argparse

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Simulates xHoundPi display proof of concept')
    config.add_argument('h_res', help='horizontal resolution', default=128)
    config.add_argument('v_res', help='gnss out file', default=64)
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    return config
