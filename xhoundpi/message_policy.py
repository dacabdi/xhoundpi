''' Policy implementations for messages '''

from typing import Any
from xhoundpi.proto_class import ProtocolClass

from .message import Message
from .message_policy_iface import IMessagePolicy

class AlwaysQualifiesPolicy(IMessagePolicy):
    '''
    Fixed value qualification, always true
    '''

    def qualifies(self, message: Message) -> bool:
        '''
        Message always qualifies
        '''
        return True

class HasLocationPolicy(IMessagePolicy):
    '''
    Classifies messages that have latitude and longitude props
    '''

    # NOTE currently we get away with non-protocol specific
    # policy because all libraries currently in use
    # use 'lat' and 'lon' for the coordinate fields

    LAT_FIELD = 'lat'
    LON_FIELD = 'lon'

    def qualifies(self, message: Message) -> bool:
        '''
        Message qualifies if it contains latitude and
        longitude information and is not in the exception lists
        '''
        return self.__has_coordinates(message.payload) and self.__is_not_exception(message)

    @classmethod
    def __has_coordinates(cls, payload: Any) -> bool:
        return hasattr(payload, 'lat') and hasattr(payload, 'lon')

    @classmethod
    def __is_not_exception(cls, msg: Message) -> bool:
        if msg.proto == ProtocolClass.NMEA:
            if not cls.__is_propietary(msg.payload):
                return msg.payload.sentence_type not in [
                    'DTM', # the lat and lon field in this msg is for offsets
                ]
        return True

    @classmethod
    def __is_propietary(cls, payload: Any):
        return hasattr(payload, 'manufacturer')
