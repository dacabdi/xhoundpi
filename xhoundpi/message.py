""" Defines Message representations """

import uuid
import typing
from dataclasses import dataclass
from .proto_class import ProtocolClass

@dataclass
class Message:
    """ Message DTO (data transfer object) """
    message_id: uuid.UUID
    proto: ProtocolClass
    payload: typing.Any
