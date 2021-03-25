""" Message set/get fields manipulation module """

from typing import List, Tuple, Any
from abc import ABC, abstractmethod

import pynmea2
import pyubx2

from .message import Message
from .status import Status

class IMessageEditor(ABC):
    """ Interface/contract for message editors """

    @abstractmethod
    def set_fields(self, message: Message, fields: List[Tuple[str, Any]]) -> Tuple[Status, Message]:
        """ Set the message payload fields using a list of substitutions """

class NMEAMessageEditor(IMessageEditor):
    """ Editor for NMEA sentences generated by the pynmea2 library """

    def set_fields(self, message: Message, fields: List[Tuple[str, Any]]) -> Tuple[Status, Message]:
        """ Set the message payload fields using a list of substitutions """
        try:
            self._set_fields(message.payload, fields)
            error = None
        except Exception as ex: # pylint: disable=broad-except
            error = ex
        return Status(error), message

    # pylint: disable=no-self-use
    def _set_fields(self, sentence: pynmea2.NMEASentence, fields: List[Tuple[str, Any]]):
        for key, value in fields:
            sentence.data[sentence.name_to_idx[key]] = value

class UBXMessageEditor(IMessageEditor):
    """ Editor for UBX messages generated by the pyubx2 library """

    def set_fields(self, message: Message, fields: List[Tuple[str, Any]]) -> Tuple[Status, Message]:
        """ Set the message payload fields using a list of substitutions """
        try:
            self._set_fields(message, fields)
            error = None
        except Exception as ex: # pylint: disable=broad-except
            error = ex
        return Status(error), message

    # pylint: disable=no-self-use
    def _set_fields(self, message: Message, fields: List[Tuple[str, Any]]):
        ubx_msg = message.payload
        ubx_msg_data = ubx_msg.__dict__
        for key, value in fields:
            if key not in ubx_msg_data.keys():
                raise AttributeError(f'UBX message with class '
                f"'0x{ubx_msg.msg_cls.hex()}', id '0x{ubx_msg.msg_id.hex()}', "
                f"and identity '{ubx_msg.identity}', "
                f"does not contain field '{key}'")
            ubx_msg_data[key] = value
        message.payload = pyubx2.UBXMessage(
            ubx_msg.msg_cls, ubx_msg.msg_id,
            ubx_msg._mode, **ubx_msg_data) # pylint: disable=protected-access
