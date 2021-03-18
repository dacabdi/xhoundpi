import unittest

from unittest.mock import Mock
from uuid import UUID

from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_serializer import (SerializerProviderError,
                                      SerializerError,
                                      ProtocolSerializerProvider,
                                      UBXProtocolSerializer,
                                      NMEAProtocolSerializer,)

class test_ProtocolSerializerProvider(unittest.TestCase):

    def test_provide(self):
        none_serializer = Mock()
        ubx_serializer = Mock()
        nmea_serializer = Mock()

        serializers = {
            ProtocolClass.NONE : none_serializer,
            ProtocolClass.UBX : ubx_serializer,
            ProtocolClass.NMEA : nmea_serializer,
        }

        provider = ProtocolSerializerProvider(serializers)

        self.assertEqual(provider.get_serializer(ProtocolClass.NONE), none_serializer)
        self.assertEqual(provider.get_serializer(ProtocolClass.UBX), ubx_serializer)
        self.assertEqual(provider.get_serializer(ProtocolClass.NMEA), nmea_serializer)

    def test_provide_no_match(self):
        none_serializer = Mock()

        serializers = {
            ProtocolClass.NONE : none_serializer,
        }

        provider = ProtocolSerializerProvider(serializers)

        self.assertEqual(provider.get_serializer(ProtocolClass.NONE), none_serializer)

        with self.assertRaises(SerializerProviderError) as context:
            provider.get_serializer(ProtocolClass.NMEA)
        self.assertEqual('No serializer available for ProtocolClass.NMEA.', str(context.exception))

class test_UBXProtocolSerializer(unittest.TestCase):

    def test_serialize(self):
        entry_point = Mock(return_value='ubx serializer')
        serializer = UBXProtocolSerializer(entry_point)

        result = serializer.serialize(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX, payload='dummy'))

        self.assertEqual(result, 'ubx serializer')
        entry_point.assert_called_once_with(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX, payload='dummy'))

    def test_serialize_error(self):
        entry_point = Mock(side_effect=Exception('internal serializer exception'))
        serializer = UBXProtocolSerializer(entry_point)

        with self.assertRaises(SerializerError) as context:
            serializer.serialize(Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload='empty'))

        entry_point.assert_called_once_with(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                    proto=ProtocolClass.UBX,
                    payload='empty'))
        self.assertEqual(
            'Error serializing message 12345678-1234-5678-1234-567812345678'
            ' with protocol ProtocolClass.UBX.',
            str(context.exception))

class test_NMEAProtocolSerializer(unittest.TestCase):

    def test_serialize(self):
        entry_point = Mock(return_value='nmea serializer')
        serializer = NMEAProtocolSerializer(entry_point)

        result = serializer.serialize(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                payload='empty', proto=ProtocolClass.NMEA))

        self.assertEqual(result, 'nmea serializer')
        entry_point.assert_called_once_with(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                payload='empty', proto=ProtocolClass.NMEA))

    def test_serialize_error(self):
        entry_point = Mock(side_effect=Exception('internal serializer exception'))
        serializer = NMEAProtocolSerializer(entry_point)

        with self.assertRaises(SerializerError) as context:
            serializer.serialize(Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA, payload='dummy'))

        entry_point.assert_called_once_with(
            Message(message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA, payload='dummy'))
        self.assertEqual(
            'Error serializing message 12345678-1234-5678-1234-567812345678'
            ' with protocol ProtocolClass.NMEA.',
            str(context.exception))
