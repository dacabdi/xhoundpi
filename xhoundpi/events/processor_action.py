""" Gnss service actions event """

import uuid

from dataclasses import dataclass
from enum import Enum

from ..proto_class import ProtocolClass

class ProcessorOp(Enum):
    """ Processor op codes """
    # pylint: disable=invalid-name
    BeginProcess = 1
    EndProcess = 2

@dataclass(order=True)
class ProcessorAction: # pylint: disable=too-many-instance-attributes
    """ Processor event schema """
    opcode: ProcessorOp
    success: bool
    processor_id: str
    activity_id: uuid.UUID
    message_id: uuid.UUID
    protocol: ProtocolClass
    details: str = ''
    schema_ver: int = 1
