''' Gnss service actions event '''

import uuid
from dataclasses import dataclass
from enum import Enum

from .common import ZERO_UUID
from ..proto_class import ProtocolClass

class GnssServiceOp(Enum):
    ''' Gnss service op codes '''
    # pylint: disable=invalid-name
    BeginRead = 1
    EndRead = 2
    BeginWrite = 3
    EndWrite = 4

@dataclass(order=True)
class GnssServiceAction:
    ''' GnssService Event schema '''
    opcode: GnssServiceOp
    success: bool
    activity_id: uuid.UUID
    details: str = ''
    message_id: uuid.UUID = ZERO_UUID
    protocol: ProtocolClass = ProtocolClass.NONE
    schema_ver: int = 1
