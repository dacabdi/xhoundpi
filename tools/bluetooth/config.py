""" Bluetooth validation tool configuration parser """

import argparse

def setup_argparser():
    """ Prepare shell arguments parser """
    config = argparse.ArgumentParser(description='Validates Bluetooth comm for xHoundPi')
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    config.add_argument('--attempt-pairing', action='store_true', dest='attempt_pair',
        help='attempt to pair to device')
    config.add_argument('--discovery-timeout', type=int, dest='discovery_timeout',
        help='device discovery timeout')
    config.add_argument('--serial', type=str, dest='serial',
        help='validating communication party')
    id_grp = config.add_mutually_exclusive_group(required=True)
    id_grp.add_argument('--address', dest='address',
        type=str, help='bluetooth device address')
    id_grp.add_argument('--name', dest='name',
        type=str, help='bluetooth device name pattern')
    return config
