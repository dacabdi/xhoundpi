""" Message operator provider """

from xhoundpi.proto_class import ProtocolClass

from .message import Message
from .operator_iface import IMessageOperator
from .operator_provider_iface import IMessageOperatorProvider

class CoordinateOperationProvider(IMessageOperatorProvider):
    """
    Message operator provider based on location type and location operation
    """

    def __init__(self,
        nmea_operator: IMessageOperator,
        ubx_operator: IMessageOperator,
        ubx_hires_operator: IMessageOperator):
        self.__nmea_opeator = nmea_operator
        self.__ubx_operator = ubx_operator
        self.__ubx_hires_operator = ubx_hires_operator

    def get_operator(self, message: Message) -> IMessageOperator:
        """
        Returns the applicable operator for
        the message based on the protocol
        and type of location information
        """
        if message.proto == ProtocolClass.NMEA:
            return self.__nmea_opeator
        if message.proto == ProtocolClass.UBX:
            # pylint: disable=using-constant-test
            if (hasattr(message.payload, 'lonHp') and hasattr(message.payload, 'latHp')):
                return self.__ubx_hires_operator
            return self.__ubx_operator
        raise ValueError(f'Cannot provide operator for protocol class \'{message.proto}\'')
