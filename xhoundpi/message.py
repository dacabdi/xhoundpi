""" Defines Message representations """

import typing
from dataclasses import dataclass
from .proto_class import ProtocolClass

@dataclass
class Message:
    """ Message DTO (data transfer object) """
    proto: ProtocolClass = ProtocolClass.NONE
    payload: typing.Any = None
