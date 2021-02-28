""" GNSS protocol frame readers module """

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple

from .proto_class import ProtocolClass

class FrameReadingError(RuntimeError):
    """ Stub to group all types of reading errors """

class MalformedFrameError(FrameReadingError):
    """ Exception type for malformed unexpected input during frame reading """

    def __init__(self, protocol: ProtocolClass, message, details=None):
        self.protocol = protocol
        self.details = details
        super().__init__(f'Error reading {protocol} frame: {message}')

class HeaderMismatchError(FrameReadingError):
    """ Exception type for header mismatch errors in the frame reader implementations """

    def __init__(self,
        headers_expected: list[bytes],
        header_received: bytes,
        protocol: ProtocolClass):
        self.protocol = protocol
        self.headers_expected = headers_expected
        self.header_received = header_received
        ex_headers_formatted = ','.join([f'\'0x{eh.hex().upper()}\'' for eh in headers_expected])
        super().__init__(f'Received header \'0x{header_received.hex().upper()}\' '\
                         f'is not in the list of acceptable headers [{ex_headers_formatted}] '\
                         f'for {protocol}.')

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
        self.__expected_headers = [expected_header]

    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Reads a preset number of bytes from the input """
        if header not in self.__expected_headers:
            raise HeaderMismatchError(self.__expected_headers, header, ProtocolClass.NONE)
        return header + stream.read(self.__message_length)

class UBXProtocolReader(IProtocolReader):
    """ UBX frame reader """

    protocol_class = ProtocolClass.UBX
    __message_preamble_size = 4
    __message_checksum_size = 2
    __expected_headers = [b'\xb5\x62']

    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Check header match and read UBX binary data frame from stream """
        if header not in self.__expected_headers:
            raise HeaderMismatchError(self.__expected_headers, header, self.protocol_class)
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
        if nbytes_read != UBXProtocolReader.__message_preamble_size:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame preamble. Read {nbytes_read} bytes '\
                f'out of {UBXProtocolReader.__message_preamble_size} expected.',
                details=preamble_bytes)
        length_bytes = preamble_bytes[2:4]
        lenght = int.from_bytes(length_bytes, "little", signed=False)
        return preamble_bytes, lenght

    @staticmethod
    def __read_body(stream: BytesIO, length: int) -> bytes:
        body = stream.read(length)
        nbytes_read = len(body)
        if nbytes_read != length:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame body. '\
                f'Read {nbytes_read} bytes out of {length} expected.',
                details=body)
        return body

    @staticmethod
    def __read_checksum(stream: BytesIO) -> bytes:
        checksum = stream.read(UBXProtocolReader.__message_checksum_size)
        nbytes_read = len(checksum)
        if nbytes_read != UBXProtocolReader.__message_checksum_size:
            raise MalformedFrameError(UBXProtocolReader.protocol_class,
                f'Found EOF attempting to read frame checksum. Read {nbytes_read} bytes '\
                f'out of {UBXProtocolReader.__message_checksum_size} expected.',
                details=checksum)
        return checksum

class NMEAProtocolReader(IProtocolReader):
    """ NMEA frame reader """

    protocol_class = ProtocolClass.NMEA

    # https://en.wikipedia.org/wiki/NMEA_0183#Message_structure
    __encoding = 'ascii'
    __max_nmea_frame_size = 82
    __end_marker = b'\x0d\x0a'
    __header_markers = [
        bytearray('$', __encoding),
        bytearray('!', __encoding)
    ]
    __extended_message_marker = bytearray('P', __encoding)

    def read_frame(self, header: bytes, stream: BytesIO) -> bytes:
        """ Check header match and read NMEA packet as binary data frame from stream """
        if header not in self.__header_markers:
            raise HeaderMismatchError(self.__header_markers, header, self.protocol_class)

        (first_byte, is_special) = NMEAProtocolReader.__read_special_marker(stream, header)
        if is_special:
            return header + NMEAProtocolReader.__read_special_frame(stream, first_byte)
        return header + NMEAProtocolReader.__read_frame(stream, first_byte)

    @staticmethod
    def __read_special_marker(stream: BytesIO, header: bytes) -> Tuple[bytes, bool]:
        """ Read first byte of the NMEA frame to determine if special vendor message """
        first_byte = stream.read(1)
        return first_byte, \
            (header == NMEAProtocolReader.__header_markers[0] \
            and first_byte == NMEAProtocolReader.__extended_message_marker)

    @staticmethod
    def __read_frame(stream: BytesIO, first_byte: bytes) -> bytes:
        """ Read NMEA packet as binary data frame from stream """
        frame = bytearray(first_byte)
        while frame[-2:] != NMEAProtocolReader.__end_marker:
            if len(frame) >= NMEAProtocolReader.__max_nmea_frame_size - 1:
                raise MalformedFrameError(NMEAProtocolReader.protocol_class,
                    f'Failed to find the frame\'s end marker of non-special message '
                    f'before the max expected size ({NMEAProtocolReader.__max_nmea_frame_size} bytes).',
                    details=frame)
            frame.extend(stream.read(1))
        return frame

    @staticmethod
    def __read_special_frame(stream: BytesIO, first_byte: bytes) -> bytes:
        """ Read special NMEA packet as binary data frame from stream """
        frame = bytearray(first_byte)
        while frame[-2:] != NMEAProtocolReader.__end_marker:
            frame.extend(stream.read(1))
        return frame

class StubProtocolReaderProvider(IProtocolReaderProvider):
    """ Provider for frame readers based on protocol class """

    def __init__(self, reader: IProtocolReader):
        """ Initialize with a fixed provider to return """
        self.__reader = reader

    def get_reader(self, protocol: ProtocolClass) -> IProtocolReader:
        """ Return message reader """
        return self.__reader
