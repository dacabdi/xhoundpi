''' Serial emulator for tests and stubs '''

from abc import ABC, abstractmethod
from io import BytesIO
from typing import TextIO

class ISerial(ABC):
    ''' Interface/contract for serial transport implementations '''

    @abstractmethod
    def read(self, size) -> bytes:
        ''' Read n bytes from the serial transport '''

    @abstractmethod
    def write(self, data: bytes) -> int:
        ''' Write n bytes to the serial transport '''

class StubSerialBinary(ISerial):
    ''' Serial implementation reading and writing circularly '''

    def __init__(self, rx: BytesIO, tx: BytesIO):
        ''' NOTE an rx stream with length zero would cause an infinite loop upon reading
        with real (non-stubbed) serial implementation, this won't be a problem because
        the OS provides locked reading behavior on exhausted streams and the coroutines
        can be unscheduled '''
        self.__transport_rx = BytesIO(b'\x00') \
            if isinstance(rx, BytesIO) and rx.getbuffer().nbytes == 0 \
            else rx
        self.__transport_tx = tx

    def read(self, size=1):
        ''' Read n bytes from the stream
        NOTE: this stub will cause an infinite
        reading loop on an empty stream,
        blocking behavior is controlled
        by the OS '''
        data = bytearray()
        while size > 0:
            read = self.__transport_rx.read(size)
            if len(read) != size:
                self.__transport_rx.seek(0)
            data.extend(read)
            size -= len(read)
        return data

    def write(self, data: bytearray):
        ''' Write n bytes to the stream '''
        return self.__transport_tx.write(data)

class StubSerialText(ISerial):
    ''' Serial implementation reading and writing circularly '''

    def __init__(self, rx: TextIO, tx: TextIO):
        ''' NOTE an rx stream with length zero would cause an infinite loop upon reading
        with real (non-stubbed) serial implementation, this won't be a problem because
        the OS provides locked reading behavior on exhausted streams and the coroutines
        can be unscheduled '''
        self.__transport_rx = rx
        self.__transport_tx = tx

    def read(self, size=1):
        ''' Read n bytes from the stream
        NOTE: this stub will cause an infinite
        reading loop on an empty stream,
        blocking behavior is controlled
        by the OS '''
        data = ''
        while size > 0:
            read = self.__transport_rx.read(size)
            if len(read) != size:
                self.__transport_rx.seek(0)
            data += read
            size -= len(read)
        return data

    def write(self, data: str):
        ''' Write n bytes to the stream '''
        return self.__transport_tx.write(data)
