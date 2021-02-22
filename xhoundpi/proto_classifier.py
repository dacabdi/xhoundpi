""" GNSS Protocol Classifiers """

from io import BytesIO
from enum import Enum

class ProtocolClass(Enum):
    NONE = 0
    UBX = 1
    NMEA = 2

class StubProtocolClassifier():
    """ Stub for a GNSS message protocol classifier """

    def __init__(self, stub_value: ProtocolClass=ProtocolClass.NONE):
        """ Set a default value to classify """
        self.stub_value = stub_value

    def classify(self, stream: BytesIO):
        """ Read until protocol identified and
        return read bytes and classification """
        return (b'', self.stub_value)