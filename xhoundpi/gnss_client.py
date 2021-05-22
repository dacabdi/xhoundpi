''' GNSS client '''

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union

from .serial import ISerial

class IGnssClient(ABC):
    ''' Interface for GNSS client implementations '''

    @abstractmethod
    def read(self, size) -> bytes:
        ''' Read n bytes from GNSS device transport '''

    @abstractmethod
    def write(self, data: bytes) -> int:
        ''' Write bytes to GNSS device transport '''

class GnssClient(IGnssClient):
    ''' Gnss client implementation facade '''

    def __init__(self, serial: Union[ISerial, BytesIO]):
        self.__serial = serial

    def read(self, size: int=1) -> bytes:
        ''' Read n bytes from GNSS serial iface '''
        return self.__serial.read(size)

    def write(self, data: bytes) -> int:
        ''' Write n bytes to GNSS serial iface '''
        return self.__serial.write(data)
