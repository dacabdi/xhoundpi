""" GNSS protocol frame readers module """

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple

from .proto_class import ProtocolClass

class MalformedFrameError(RuntimeError):
    """ Exception type for malformed unexpected input during frame reading """

    def __init__(self, protocol: ProtocolClass, message):
        super().__init__(f'Error reading {protocol} frame: {message}')

class HeaderMismatchError(RuntimeError):
    """ Exception type for header mismatch errors in the frame reader implementations """

    def __init__(self,
        header_expected: bytes,
        header_received: bytes,
        protocol: ProtocolClass=ProtocolClass.NONE):
        super().__init__(f'Expected header {header_expected} for protocol '\
                         f'{protocol} and received {header_received}')

class IProtocolReader(ABC):
    """ Interface/contract for protocol reader implementations """

    @abstractmethod
    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Reads a frame body assuming header was already consumed """

class IProtocolReaderProvider(ABC):
    """ Interface/contract for protocol reader provider implementations """

    @abstractmethod
    def get_reader(self, protocol: ProtocolClass) -> IProtocolReader:
        """ Selects a protocol reader based on the protocol class """

class StubProtocolReader(IProtocolReader):
    """ Stub for a GNSS message reader """

    def __init__(self, message_length: int=1, expected_header: bytes=b'\x00'):
        """ Initialize with a set number of bytes to read and a preset header expected """
        self.__message_length = message_length
        self.__expected_header = expected_header

    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Reads a preset number of bytes from the input """
        if header != self.__expected_header:
            raise HeaderMismatchError(header, self.__expected_header)
        return header + stream.read(self.__message_length)

class UBXProtocolReader(IProtocolReader):
    """ UBX frame reader """

    protocol_class = ProtocolClass.UBX
    __message_preamble_size = 4
    __message_checksum_size = 2
    __expected_header = b'\xb5\x62'

    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Read UBX packet binary data frame from stream """
        if header != self.__expected_header:
            raise HeaderMismatchError(header, self.__expected_header, self.protocol_class)
        return header + UBXProtocolReader.__read_frame(stream)

    @staticmethod
    def __read_frame(stream: BytesIO) -> bytes:
        preamble, length = UBXProtocolReader.__read_preamble(stream)
        body = UBXProtocolReader.__read_body(stream, length)
        checksum = UBXProtocolReader.__read_checksum(stream)
        return preamble + body + checksum

    @staticmethod
    def __read_preamble(stream: BytesIO) -> Tuple[bytes, int]:
        preamble_bytes = stream.read(UBXProtocolReader.__message_preamble_size)
        nbytes_read = len(preamble_bytes)
        if nbytes_read < UBXProtocolReader.__message_preamble_size:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame preamble. Read {nbytes_read} bytes'\
                f'out of {UBXProtocolReader.__message_preamble_size} expected.')
        length_bytes = preamble_bytes[2:4]
        lenght = int.from_bytes(length_bytes, "little", signed=False)
        return preamble_bytes, lenght

    @staticmethod
    def __read_body(stream: BytesIO, length: int) -> bytes:
        body = stream.read(length)
        nbytes_read = len(body)
        if nbytes_read < length:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame body. '\
                f'Read {nbytes_read} bytes out of {length} expected.')
        return body

    @staticmethod
    def __read_checksum(stream: BytesIO) -> bytes:
        checksum = stream.read(UBXProtocolReader.__message_preamble_size)
        nbytes_read = len(checksum)
        if nbytes_read < UBXProtocolReader.__message_checksum_size:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame checksum. Read {nbytes_read} bytes'\
                f'out of {UBXProtocolReader.__message_checksum_size} expected.')
        return checksum

class StubProtocolReaderProvider(IProtocolReaderProvider):
    """ Provider for frame readers based on protocol class """

    def __init__(self, reader: IProtocolReader):
        """ Initialize with a fixed provider to return """
        self.__reader = reader

    def get_reader(self, protocol: ProtocolClass) -> IProtocolReader:
        """ Return message reader """
        return self.__reader
