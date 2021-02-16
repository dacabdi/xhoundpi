"""xHoundPi firmware execution module"""

from .config import setup_configparser

def main():
    """xHoundPi entry point"""
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

main()
