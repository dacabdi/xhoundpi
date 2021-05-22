''' GNSS protocol serializers '''

from abc import ABC, abstractmethod
from typing import Callable

from .proto_class import ProtocolClass
from .message import Message

class SerializerProviderError(RuntimeError):
    ''' Exception type for unsatisfiable serializer protocol type '''

    def __init__(self, protocol: ProtocolClass, details=None):
        self.protocol = protocol
        self.details = details
        super().__init__(f'No serializer available for {protocol}.')

class SerializerError(RuntimeError):
    ''' Exception type for serializer errors '''

    def __init__(self, message: Message, details=None):
        self.message = message
        self.details = details
        super().__init__(f'Error serializing message {message.message_id} '
                         f'with protocol {message.proto}.')

class IProtocolSerializer(ABC):
    ''' Interface/contract for protocol serializer implementations '''

    @abstractmethod
    def serialize(self, message: Message) -> bytes:
        ''' Serialize the message into a byte array '''

class IProtocolSerializerProvider(ABC):
    ''' Interface/contract for protocol serializer provider implementations '''

    @abstractmethod
    def get_serializer(self, protocol: ProtocolClass) -> IProtocolSerializer:
        ''' Choses a serializer based on the protocol class '''

class UBXProtocolSerializer(IProtocolSerializer):
    ''' UBX protocol serializer proxy '''

    protocol_class = ProtocolClass.UBX

    def __init__(self, serializer_lib_entry_point: Callable[[Message], bytes]):
        self.__serializer_lib_entry_point = serializer_lib_entry_point

    def serialize(self, message: Message) -> bytes:
        ''' Serialize the UBX message into a byte array '''
        try:
            return self.__serializer_lib_entry_point(message)
        except Exception as ex:
            raise SerializerError(message) from ex

class NMEAProtocolSerializer(IProtocolSerializer):
    ''' NMEA 0183 protocol serializer proxy '''

    protocol_class = ProtocolClass.NMEA
    protocol_revision = 'NMEA-0183'

    def __init__(self, serializer_lib_entry_point: Callable[[Message], bytes]):
        self.__serializer_lib_entry_point = serializer_lib_entry_point

    def serialize(self, message: Message) -> bytes:
        ''' Serialize the NMEA message into a byte array '''
        try:
            return self.__serializer_lib_entry_point(message)
        except Exception as ex:
            raise SerializerError(message) from ex

class ProtocolSerializerProvider(IProtocolSerializerProvider):
    ''' Protocol serializer provider based on a static mapping provided on init '''

    def __init__(self, mapping: dict):
        self.__mapping = mapping

    def get_serializer(self, protocol: ProtocolClass) -> IProtocolSerializer:
        ''' Return mapped parser for the protocol provided '''
        try:
            return self.__mapping[protocol]
        except KeyError as ex:
            raise SerializerProviderError(protocol=protocol) from ex
