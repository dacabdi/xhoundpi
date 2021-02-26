""" GNSS protocol classifiers and parsers """

from io import BytesIO
from abc import ABC, abstractmethod
from typing import Tuple, Any

from .proto_class import ProtocolClass
from .message import Message

class IProtocolClassifier(ABC):

    @abstractmethod
    def classify(self, stream: BytesIO) -> ProtocolClass:
        pass

class IProtocolParser(ABC):

    @abstractmethod
    def parse(self, stream: BytesIO) -> Tuple[bytes, Any]:
        pass

class IProtocolParserProvider(ABC):

    @abstractmethod
    def get_parser(self, protocol: ProtocolClass) -> IProtocolParser:
        pass

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

