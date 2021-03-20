""" Gnss service actions event """

import uuid
from dataclasses import dataclass
from enum import Enum

from .common import ZERO_UUID
from ..proto_class import ProtocolClass

class GnssServiceActionCode(Enum):
    """ Gnss service runner action op codes """
    READ_BEGIN = 1
    READ_END = 2
    WRITE_BEGIN = 3
    WRITE_END = 4
    START = 5
    END = 6

@dataclass(order=True)
class GnssServiceAction:
    """ Message DTO (data transfer object) """
    opcode: GnssServiceActionCode
    success: bool
    activity_id: uuid.UUID
    details: str = ''
    message_id: uuid.UUID = ZERO_UUID
    protocol: ProtocolClass = ProtocolClass.NONE
    schema_ver: int = 1
