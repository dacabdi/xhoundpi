import unittest
from io import BytesIO

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import (StubProtocolClassifier,
                                      ProtocolClassifier,
                                      ProtocolClassificationError,)

class test_StubProtocolClassifier(unittest.TestCase):

    def test_classify(self):
        header_source = BytesIO(b'H')
        classifier = StubProtocolClassifier(ProtocolClass.UBX)

        self.assertEqual(classifier.classify(header_source), (b'H', ProtocolClass.UBX))

class test_ProtocolClassifier(unittest.TestCase):

    def test_classify(self):
        stream = BytesIO(b'\x24\xb5\x62\x00')
        classifier = ProtocolClassifier({
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX,
            bytes(b'\x00') : ProtocolClass.NONE
        })

        self.assertEqual(classifier.classify(stream), (bytes(b'\x24'), ProtocolClass.NMEA))
        self.assertEqual(classifier.classify(stream), (bytes(b'\xb5\x62'), ProtocolClass.UBX))
        self.assertEqual(classifier.classify(stream), (bytes(b'\x00'), ProtocolClass.NONE))

    def test_classify_fails_if_past_classification_point(self):
        stream = BytesIO(b'\x00\x00\x00\x24\xb5\x62\x00')
        classifier = ProtocolClassifier({
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX,
            bytes(b'\x01') : ProtocolClass.NONE
        })

        with self.assertRaises(ProtocolClassificationError) as context:
            classifier.classify(stream)

        self.maxDiff = None
        self.assertEqual("Error identifying protocol from header. Read bytes '0x0000' not among expected headers ['0x24','0xB562','0x01'].", str(context.exception))
        self.assertEqual(context.exception.data_read, b'\x00\x00')
        self.assertEqual(context.exception.mapping, {
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX,
            bytes(b'\x01') : ProtocolClass.NONE
        })
