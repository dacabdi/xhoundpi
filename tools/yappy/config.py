''' Serial stream validation tool configuration parser '''

import argparse

def setup_argparser():
    ''' Prepares shell arguments parser '''
    config = argparse.ArgumentParser(
        description='Validates serial communication between two devices')
    config.add_argument('--serial_a', type=str, dest='serial_a',
        help='serial stream device A')
    config.add_argument('--serial_b', dest='serial_b', type=str,
        help='serial stream device B')
    config.add_argument('--baudrate', dest='baudrate', type=int, default=115200,
        help='baudrate for both parties')
    return config
