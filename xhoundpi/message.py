""" Defines Message representations """

import typing
from dataclasses import dataclass
from .proto_class import ProtocolClass

@dataclass
class Message:
    proto: ProtocolClass = ProtocolClass.NONE
    header: bytes = b''
    raw: bytes = b''
    msg: 'typing.Any' = None