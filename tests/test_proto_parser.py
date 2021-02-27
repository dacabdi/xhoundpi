import unittest
from io import BytesIO

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import StubProtocolClassifier
from xhoundpi.proto_parser import StubParserProvider, StubProtocolParser

class test_StubProtocolClassifier(unittest.TestCase):

    def test_classify(self):
        header_source = BytesIO(b'H')
        classifier = StubProtocolClassifier(ProtocolClass.UBX)

        self.assertEqual(classifier.classify(header_source), (b'H', ProtocolClass.UBX))

class test_StubProtocolParser(unittest.TestCase):

    def test_parse(self):
        data_source = b'\x01\x02'
        parser = StubProtocolParser()

        self.assertEqual(parser.parse(data_source), b'\x01\x02')

class test_StubParserProvider(unittest.TestCase):

    def test_provide_parser(self):
        stub_parser = StubProtocolParser()
        parser_provider = StubParserProvider(stub_parser)

        self.assertEqual(parser_provider.get_parser(ProtocolClass.NONE), stub_parser)
