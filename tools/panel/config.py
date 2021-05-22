''' Panel proof of concept configuration parser module '''

import argparse

def setup_argparser():
    ''' Prepare shell arguments parser '''
    config = argparse.ArgumentParser(description='Simulates xHoundPi display proof of concept')
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    config.add_argument('--display-height', dest='display_height', type=int, default=64,
        help='display height in pixels')
    config.add_argument('--display-width', dest='display_width', type=int, default=256,
        help='display width in pixels')
    config.add_argument('--mode', dest='mode', type=str, default='rgb',
        help='display depth mode, valid values are "rgb", "grayscale", and "1bit"')
    config.add_argument('--scale', dest='scale', type=int, default=4,
        help='display scaling for fake displays')
    config.add_argument('--driver', dest='driver', type=str, default='pygame',
        help='type of display to drive')
    return config
