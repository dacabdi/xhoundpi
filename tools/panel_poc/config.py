""" Panel proof of concept configuration parser module """

import argparse

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Simulates xHoundPi display proof of concept')
    config.add_argument('h_res', help='horizontal resolution', default=128)
    config.add_argument('v_res', help='gnss out file', default=64)
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    config.add_argument('--display-height', dest='display_height', type=int, default=64,
        help='display height in pixels')
    config.add_argument('--display-width', dest='display_width', type=int, default=256,
        help='display width in pixels')
    return config
