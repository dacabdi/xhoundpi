""" Gnss service runner actions event """

import uuid
from dataclasses import dataclass
from enum import Enum

from .common import ZERO_UUID
from ..proto_class import ProtocolClass

class GnssServiceRunnerActionOpCode(Enum):
    """ Gnss service runner action op codes """
    READ_BEGIN = 1
    READ_END = 2
    WRITE_BEGIN = 3
    WRITE_END = 4
    START = 5
    END = 6

@dataclass(order=True)
class GnssServiceRunnerAction:
    """ Message DTO (data transfer object) """
    opcode: GnssServiceRunnerActionOpCode
    message_id: uuid.UUID = ZERO_UUID
    protocol: ProtocolClass = ProtocolClass.NONE
    ver: int = 1
