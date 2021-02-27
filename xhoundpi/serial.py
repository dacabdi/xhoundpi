""" Serial emulator for tests and stubs """

from abc import ABC, abstractmethod
from io import BytesIO

class ISerial(ABC):
    """ Interface/contract for serial transport implementations """

    @abstractmethod
    def read(self, size) -> bytes:
        """ Read n bytes from the serial transport """

    @abstractmethod
    def write(self, data: bytes) -> int:
        """ Write n bytes to the serial transport """

class StubSerial(ISerial):
    """ Serial implementation reading and writing circularly """

    def __init__(self, rx: BytesIO, tx: BytesIO):
        self.transport_rx = rx
        self.transport_tx = tx

    def open(self):
        """ Open the tx and rx transport streams """
        self.transport_rx.open(mode='rb')
        self.transport_tx.open(mode='+wb')

    def close(self):
        """ Close the tx and rx transport streams """
        self.transport_rx.close()
        self.transport_tx.close()

    def read(self, size=1):
        """ Read n bytes from the stream """
        data = []
        while size > 0:
            read = self.transport_rx.read(size)
            if len(read) != size:
                self.transport_rx.seek(0)
            data.extend(read)
            size -= len(read)
        return data

    def write(self, data: bytearray):
        """ Write n bytes to the stream """
        return self.transport_tx.write(data)
