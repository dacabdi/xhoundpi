import unittest
from io import BytesIO
from xhoundpi.proto_classifier import ProtocolClass, StubProtocolClassifier

class test_StubProtocolClassifier(unittest.TestCase):

    def test_classify(self):
        header_source = BytesIO()
        classifier = StubProtocolClassifier(ProtocolClass.UBX)
        self.assertEqual(classifier.classify(header_source), (b'', ProtocolClass.UBX))