''' GNSS client '''

import uuid

from typing import Tuple

from .gnss_service_iface import IGnssService
from .gnss_client import IGnssClient
from .proto_classifier import IProtocolClassifier
from .proto_reader import IProtocolReaderProvider
from .proto_parser import IProtocolParserProvider
from .proto_serializer import IProtocolSerializerProvider
from .status import Status
from .message import Message


class GnssService(IGnssService):
    ''' Gnss service facade '''

    def __init__( # pylint: disable=too-many-arguments
        self,
        gnss_client: IGnssClient,
        classifier: IProtocolClassifier,
        reader_provider: IProtocolReaderProvider,
        parser_provider: IProtocolParserProvider,
        serializer_provider: IProtocolSerializerProvider):
        self.__gnss_client = gnss_client
        self.__classifier = classifier
        self.__reader_provider = reader_provider
        self.__parser_provider = parser_provider
        self.__serializer_provider = serializer_provider

    async def read_message(self) -> Tuple[Status, Message]:
        ''' Reads, classifies, and parses input from the GNSS client stream '''
        try:
            (header, protocol) = self.__classifier.classify(self.__gnss_client)
            reader = self.__reader_provider.get_reader(protocol)
            parser = self.__parser_provider.get_parser(protocol)
            frame = reader.read_frame(header, self.__gnss_client)
            payload = parser.parse(frame)
            return Status.OK(), Message(proto=protocol, payload=payload, message_id=uuid.uuid4())
        except Exception as err: # pylint: disable=broad-except
            return Status(err), None

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        ''' Writes messages as byte strings to the GNSS client input '''
        try:
            serializer = self.__serializer_provider.get_serializer(message.proto)
            data = serializer.serialize(message)
            cbytes = self.__gnss_client.write(data)
            return Status.OK(), cbytes
        except Exception as err: # pylint: disable=broad-except
            return Status(err), 0
