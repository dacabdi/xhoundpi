# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=duplicate-code

import unittest
from unittest.mock import MagicMock

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_parser import ProtocolParserProvider,\
                                  StubParserProvider, \
                                  StubProtocolParser, \
                                  UBXProtocolParser, \
                                  NMEAProtocolParser

class test_StubProtocolParser(unittest.TestCase):

    def test_parse(self):
        data_source = b'\x01\x02'
        parser = StubProtocolParser()

        self.assertEqual(parser.parse(data_source), b'\x01\x02')

class test_UBXProtocolParser(unittest.TestCase):

    def test_parse(self):
        parser_lib_entry_point = MagicMock(return_value='parsed message')
        parser = UBXProtocolParser(parser_lib_entry_point)
        self.assertEqual(parser.parse(b'abc'), 'parsed message')
        parser_lib_entry_point.assert_called_once_with(b'abc')

class test_NMEAProtocolParser(unittest.TestCase):

    def test_parse(self):
        parser_lib_entry_point = MagicMock(return_value='parsed message')
        parser = NMEAProtocolParser(parser_lib_entry_point)
        self.assertEqual(parser.parse(b'abc'), 'parsed message')
        parser_lib_entry_point.assert_called_once_with(b'abc')

class test_StubParserProvider(unittest.TestCase):

    def test_provide_parser(self):
        stub_parser = StubProtocolParser()
        parser_provider = StubParserProvider(stub_parser)

        self.assertEqual(parser_provider.get_parser(ProtocolClass.NONE), stub_parser)
