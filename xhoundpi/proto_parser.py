""" GNSS protocol classifiers and parsers """

from io import BytesIO
from abc import ABC, abstractmethod
from typing import Tuple, Any

from .proto_class import ProtocolClass

class IProtocolClassifier(ABC):
    """ Interface/contract for protocol classifier implementations """

    @abstractmethod
    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Determine the protocol by reading the first few bytes of the stream
        and returnt the bytes read and the protocol classification"""

class IProtocolParser(ABC):
    """ Interface/contract for protocol parser implementations """

    @abstractmethod
    def parse(self, stream: BytesIO) -> Tuple[bytes, Any]:
        """ Consume and parse the stream to produce a deserialized
        representation that matches the class of the protocol.
        Must return the deserialized message and the raw bytes read """

class IProtocolParserProvider(ABC):
    """ Interface/contract for protocol parser provider implementations """

    @abstractmethod
    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        """ Choses a parser based on the protocol class """

class StubProtocolClassifier():
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, stub_value: ProtocolClass):
        """ Set a default value to classify """
        self.stub_value = stub_value

    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Reads a line and returns a fixed setup protocol value """
        return (stream.read(1), self.stub_value)

class StubProtocolParser(IProtocolParser):
    """ Stub for message parser """

    def parse(self, stream: BytesIO) -> Tuple[bytes, Any]:
        return (stream.read(1), None)

class StubParserProvider(IProtocolParserProvider):
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, parser: IProtocolParser):
        self.parser = parser

    def get_parser(self, protocol: ProtocolClass) -> IProtocolParserProvider:
        """ Provide parser according to protocol class """
        return self.parser
