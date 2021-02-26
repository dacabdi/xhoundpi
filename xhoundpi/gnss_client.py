""" GNSS client """

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union

from .serial import ISerial

class IGnssClient(ABC):

    @abstractmethod
    def read(self, size) -> bytes:
        pass

    @abstractmethod
    def write(self, data: bytes) -> int:
        pass

class GnssClient(IGnssClient):
    """ Gnss client implementation facade """

    def __init__(self, serial: Union[ISerial, BytesIO]):
        self.serial = serial

    def read(self, size: int=1) -> bytes:
        """ Read n bytes from GNSS serial iface """
        return self.serial.read(size)

    def write(self, data: bytes) -> int:
        """ Write n bytes to GNSS serial iface """
        return self.serial.write(data)
