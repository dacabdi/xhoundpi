""" Serial emulator for tests and stubs """

import io
from itertools import cycle

class StubSerial():
    """ Serial implementation reading and writing circularly """

    def __init__(self, rx: bytearray=[], tx: bytearray=[]):
        self.rx = rx
        self.rx_it = cycle(self.rx)
        self.tx = tx

    def open(self):
        pass

    def close(self):
        pass

    def read(self, size=1):
        """ Read n bytes from the Rx iterable """
        data = []
        while len(data) < size:
            data.append(next(self.rx_it))
        return data

    def write(self, data: bytearray):
        """ Append n bytes to the Tx container """
        self.tx.extend(data)
        return len(data)

