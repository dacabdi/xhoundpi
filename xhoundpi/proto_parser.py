""" GNSS protocol parsers """

from abc import ABC, abstractmethod
from typing import Tuple, Any
from pyubx2 import UBXReader
from pyubx2.ubxtypes_core import GET

from .proto_class import ProtocolClass

class IProtocolParser(ABC):
    """ Interface/contract for protocol parser implementations """

    @abstractmethod
    def parse(self, frame: bytes) -> Tuple[Any]:
        """ Parse the frame byte array into a DTO """

class IProtocolParserProvider(ABC):
    """ Interface/contract for protocol parser provider implementations """

    @abstractmethod
    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        """ Choses a parser based on the protocol class """

class StubProtocolParser(IProtocolParser):
    """ Stub for message parser """

    def parse(self, frame: bytes) -> Tuple[Any]:
        return frame

class UBXProtocolParser(IProtocolParser):
    """ UBX protocol parser proxy """

    def parse(self, frame: bytes) -> Tuple[Any]:
        # TODO the parser libary should not be an implicit dependency
        """ Parse the UBX frame byte array into a UBXMessage """
        return UBXReader.parse(frame, validate=True, mode=GET)

class StubParserProvider(IProtocolParserProvider):
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, parser: IProtocolParser):
        self.parser = parser

    def get_parser(self, protocol: ProtocolClass) -> IProtocolParserProvider:
        """ Provide parser according to protocol class """
        return self.parser
