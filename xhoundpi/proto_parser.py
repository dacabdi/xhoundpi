''' GNSS protocol parsers '''

from abc import ABC, abstractmethod
from typing import Callable, Any

from .proto_class import ProtocolClass

class IProtocolParser(ABC):
    ''' Interface/contract for protocol parser implementations '''

    @abstractmethod
    def parse(self, frame: bytes) -> Any:
        ''' Parse the frame byte array into a DTO '''

class IProtocolParserProvider(ABC):
    ''' Interface/contract for protocol parser provider implementations '''

    @abstractmethod
    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        ''' Choses a parser based on the protocol class '''

class StubProtocolParser(IProtocolParser):
    ''' Stub for message parser '''

    def parse(self, frame: bytes) -> Any:
        return frame

class UBXProtocolParser(IProtocolParser):
    ''' UBX protocol parser proxy '''

    protocol_class = ProtocolClass.UBX

    def __init__(self, parser_lib_entry_point: Callable[[bytes], Any]):
        self.__parser_lib_entry_point = parser_lib_entry_point

    def parse(self, frame: bytes) -> Any:
        ''' Parse the UBX frame byte array into a deserialized message '''
        return self.__parser_lib_entry_point(frame)

class NMEAProtocolParser(IProtocolParser):
    ''' NMEA 0183 protocol parser proxy '''

    protocol_class = ProtocolClass.NMEA
    protocol_revision = 'NMEA-0183'

    def __init__(self, parser_lib_entry_point: Callable[[bytes], Any]):
        self.__parser_lib_entry_point = parser_lib_entry_point

    def parse(self, frame: bytes) -> Any:
        ''' Parse the NMEA frame byte array into a deserialized message '''
        return self.__parser_lib_entry_point(frame)

class StubParserProvider(IProtocolParserProvider):
    ''' Stub for a GNSS message protocol classifier '''

    def __init__(self, parser: IProtocolParser):
        self.__parser = parser

    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        ''' Provide parser according to protocol class '''
        return self.__parser

class ProtocolParserProvider(IProtocolParserProvider):
    ''' Protocol parser provider based on a static mapping provided on init '''

    def __init__(self, mapping: dict):
        self.__mapping = mapping

    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        ''' Return mapped parser for the protocol provided '''
        return self.__mapping[protocol]
