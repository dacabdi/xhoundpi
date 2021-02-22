""" Serial emulator for tests and stubs """

from io import BytesIO

class StubSerial():
    """ Serial implementation reading and writing circularly """

    def __init__(self, rx: BytesIO, tx: BytesIO):
        self.rx = rx
        self.tx = tx

    def open(self):
        self.rx.open(mode='rb')
        self.tx.open(mode='+wb')

    def close(self):
        self.rx.close()
        self.rx.close()

    def read(self, size=1):
        """ Read n bytes from the stream """
        data = []
        while size > 0:
            read = self.rx.read(size)
            if len(read) != size:
                self.rx.seek(0)
            data.extend(read)
            size -= len(read)
        return data

    def write(self, data: bytearray):
        """ Write n bytes to the stream """
        return self.tx.write(data)

