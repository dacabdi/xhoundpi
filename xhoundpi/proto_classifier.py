""" Protocol classification module """

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple

from .proto_class import ProtocolClass

class IProtocolClassifier(ABC):
    """ Interface/contract for protocol classifier implementations """

    @abstractmethod
    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Determine the protocol by reading the first few bytes of the stream
        and returnt the bytes read and the protocol classification"""

class StubProtocolClassifier():
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, stub_value: ProtocolClass):
        """ Set a default value to classify """
        self.stub_value = stub_value

    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Reads a line and returns a fixed setup protocol value """
        return (stream.read(1), self.stub_value)
