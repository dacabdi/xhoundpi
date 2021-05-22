''' Message fields manipulation module '''

from typing import Dict, Tuple

import pynmea2
import pyubx2

from .message import Message
from .status import Status
from .message_editor_iface import IMessageEditor

class NMEAMessageEditor(IMessageEditor):
    ''' Editor for NMEA sentences generated by the pynmea2 library '''

    def set_fields(self, message: Message, fields: Dict) -> Tuple[Status, Message]:
        ''' Set the message payload fields using a list of substitutions '''
        try:
            self._set_fields(message.payload, fields)
            error = None
        except KeyError as ex:
            error = AttributeError(
                f"NMEA sentence '{message.payload.identifier()}' "
                f"does not contain field '{ex.args[0]}'")
        return Status(error), message

    # pylint: disable=no-self-use
    def _set_fields(self, sentence: pynmea2.NMEASentence, fields: Dict):
        for key, value in fields.items():
            sentence.data[sentence.name_to_idx[key]] = value

class UBXMessageEditor(IMessageEditor):
    ''' Editor for UBX messages generated by the pyubx2 library '''

    def set_fields(self, message: Message, fields: Dict) -> Tuple[Status, Message]:
        ''' Set the message payload fields using a list of substitutions '''
        try:
            self._set_fields(message, fields)
            error = None
        except AttributeError as ex:
            error = ex
        return Status(error), message

    # pylint: disable=no-self-use
    def _set_fields(self, message: Message, fields: Dict):
        ubx_msg = message.payload
        ubx_msg_data = ubx_msg.__dict__
        for key, value in fields.items():
            if key not in ubx_msg_data.keys():
                raise AttributeError(f'UBX message with class '
                f"'0x{ubx_msg.msg_cls.hex()}', id '0x{ubx_msg.msg_id.hex()}', "
                f"and identity '{ubx_msg.identity}', "
                f"does not contain field '{key}'")
            ubx_msg_data[key] = value
        message.payload = pyubx2.UBXMessage(
            ubx_msg.msg_cls, ubx_msg.msg_id,
            ubx_msg._mode, **ubx_msg_data) # pylint: disable=protected-access
