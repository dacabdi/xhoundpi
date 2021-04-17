""" Device data capture processing tools """
# pylint: disable=wrong-import-position

# print debugging information
# before loadint anything
import os
import sys
import pprint
pprint.pprint(os.getcwd())
pprint.pprint(sys.path)
pprint.pprint(dict(os.environ), width=1)

import argparse
from .parser import parser

def main():
    """ Entry point for the processor """
    config = setup_argparser()
    options = config.parse_args()
    with open(options.input, 'r', encoding='utf8') as input_file,\
         open(options.output, 'wb') as output_file:
        parser(input_file, output_file)

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Process device serial captures into binary files')
    config.add_argument('input', metavar='FILE', type=str,
        help='ascii input file to process')
    config.add_argument('output', metavar='FILE', type=str,
        help='binary output file')
    return config

main()
