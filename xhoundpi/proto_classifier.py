""" Protocol classification module """

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple

from .proto_class import ProtocolClass

class ProtocolClassificationError(RuntimeError):
    """ Error representation for protocol header classification errors """

    def __init__(self, data: bytes, mapping: dict):
        self.data_read = data
        self.mapping = mapping
        expected_headers = ','.join([f'\'0x{eh.hex().upper()}\'' for eh in mapping.keys()])
        super().__init__(f'Error identifying protocol from header. '
            f'Read bytes \'0x{data.hex().upper()}\' not among '
            f'expected headers [{expected_headers}].')

class IProtocolClassifier(ABC):
    """ Interface/contract for protocol classifier implementations """

    @abstractmethod
    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Determine the protocol by reading the first few bytes of the stream
        and returnt the bytes read and the protocol classification"""

class StubProtocolClassifier(IProtocolClassifier):
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, stub_value: ProtocolClass):
        """ Set a default value to classify """
        self.__stub_value = stub_value

    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        """ Reads a line and returns a fixed setup protocol value """
        return (stream.read(1), self.__stub_value)

class ProtocolClassifier(IProtocolClassifier):
    """ Classifies protocols based on header matching """

    def __init__(self, mapping: dict):
        self.__mapping = mapping
        self.__max_size = len(max(self.__mapping.keys(), key=len))

    def classify(self, stream: BytesIO) -> Tuple[bytes, ProtocolClass]:
        data = bytearray()
        # TODO improve this, horribly inefficient (eg, if 1st byte not matching, drop already)
        while len(data) < self.__max_size:
            data.extend(stream.read(1))
            if bytes(data) in self.__mapping.keys():
                return bytes(data), self.__mapping[bytes(data)]
        raise ProtocolClassificationError(data, self.__mapping)
