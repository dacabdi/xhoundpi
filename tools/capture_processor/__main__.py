""" Device data capture processing tools """

import argparse
from .parser import parser

def main():
    """ Entry point for the processor """
    config = setup_argparser()
    options = config.parse_args()
    parser(options.input, options.output)

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Process device serial captures into binary files')
    config.add_argument('input', metavar='FILE', type=argparse.FileType('r'),
        help='ascii input file to process')
    config.add_argument('output', metavar='FILE', type=argparse.FileType('bw'),
        help='binary output file')
    return config

main()
