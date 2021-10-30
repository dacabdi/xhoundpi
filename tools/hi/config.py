import argparse

def setup_argparser():
    ''' Prepare shell arguments parser '''
    config = argparse.ArgumentParser(description='Keyboard and input buttons POC driver')
    config.add_argument('--verbose', action='store_true', dest='verbose',
        help='set log level to debug')
    return config
