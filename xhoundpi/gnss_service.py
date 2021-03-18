""" GNSS client """

import uuid

from .gnss_service_iface import IGnssService
from .gnss_client import IGnssClient
from .proto_classifier import IProtocolClassifier
from .proto_reader import IProtocolReaderProvider
from .proto_parser import IProtocolParserProvider
from .proto_serializer import IProtocolSerializerProvider
from .message import Message

class GnssService(IGnssService):
    """ Gnss service facade """

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

    async def read_message(self) -> Message:
        """ Reads, classifies, and parses input from the GNSS client stream """
        (header, protocol) = self.__classifier.classify(self.__gnss_client)
        reader = self.__reader_provider.get_reader(protocol)
        parser = self.__parser_provider.get_parser(protocol)
        frame = reader.read_frame(header, self.__gnss_client)
        payload = parser.parse(frame)
        return Message(proto=protocol, payload=payload, message_id=uuid.uuid4())

    async def write_message(self, message: Message) -> int:
        """ Writes messages as byte strings to the GNSS client input """
        serializer = self.__serializer_provider.get_serializer(message.proto)
        data = serializer.serialize(message)
        return self.__gnss_client.write(data)
