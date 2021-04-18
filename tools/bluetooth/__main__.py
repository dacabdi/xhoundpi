""" Bluetooth validation entry point """
# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position

from xhoundpi.diagnostics import describe_environment
print(describe_environment())

# standard libs
import os
import logging
import serial
import bluetooth as bt

from .config import setup_argparser

logger = logging.getLogger()

def main():
    """ Entry point for the BT validator """
    setup_logger()

    config = setup_argparser()
    options = config.parse_args()

    logger.debug(f'Configuration options: {options}')
    logger.debug(f'Current working directory "{os.getcwd()}"')
    logger.debug(f'Environment variables "{os.environ}"')

    try:
        logger.info('Scanning for BT devices')
        devices = get_devices()
        logger.info(f'Devices found: {devices}')

        logger.info('Filtering devices')
        address, name = find(options, devices)
        logger.info(f'Matching device {address}/{name}')

        pair(options, address)

        logger.info('Connecting to device...')
        sock = bt.BluetoothSocket(bt.RFCOMM)
        sock.connect((address, 1))
        logger.info('Successfully connected!')

        with pyserial.Serial(options.serial, 115200) as ser:
            while True:
                msg1 = 'test_tx'
                sock.send(msg1)
                rx_msg1 = ser.read(len(msg1))
                if rx_msg1 != msg1:
                    raise ValueError(f"Mismatch! '{msg1}' != '{rx_msg1}'")
                msg2 = 'test_tx'
                ser.write(msg2)
                rx_msg2 = sock.recv(len(msg2))
                if rx_msg2 != msg2:
                    raise ValueError(f"Mismatch! '{msg2}' != '{rx_msg2}'")

    except Exception: # pylint: disable=broad-except
        logger.exception("Blueetooth validator failed")
    finally:
        sock.close()

def pair(options, address): # pylint: disable=unused-argument
    if not options.attempt_pairing:
        logger.warning('Pairing not requested')
        return
    if sys.platform == 'win32':
        raise NotImplementedError('Pairing programmatically'
                                  'not implemented for Windows OS')
    raise NotImplementedError('Pairing programmatically'
                              'not implemented for Linux')

def get_devices():
    return bt.discover_devices(
        lookup_names=True,
        duration=20)

def find(options, devices):
    if options.address:
        return find_by_address(options.address, devices)
    return find_by_name(options.name, devices)

def find_by_address(address, devices):
    for (_address, _name) in devices:
        if address == _address:
            return (_address, _name)
    raise RuntimeError(f'Device not found with address \'{address}\'')

def find_by_name(name, devices):
    for (_addr, _name) in devices:
        if name in _name:
            return (_addr, _name)
    raise RuntimeError(f'Device not found with name like \'{name}\'')

def setup_logger():
    """ Basic logger configuration """
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

main()
