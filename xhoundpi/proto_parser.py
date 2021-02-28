""" GNSS protocol parsers """

from abc import ABC, abstractmethod
from typing import Tuple, Any

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

    def __init__(self, parser_lib_entry_point: callable):
        self.__parser_lib_entry_point = parser_lib_entry_point

    def parse(self, frame: bytes) -> Tuple[Any]:
        """ Parse the UBX frame byte array into a deserialized message """
        return self.__parser_lib_entry_point(frame)

class StubParserProvider(IProtocolParserProvider):
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, parser: IProtocolParser):
        self.__parser = parser

    def get_parser(self, protocol: ProtocolClass) -> IProtocolParserProvider:
        """ Provide parser according to protocol class """
        return self.__parser
