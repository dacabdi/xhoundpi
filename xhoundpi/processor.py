""" Defines GNSS service interface/contracts """

from typing import Tuple

from .message import Message
from .status import Status
from .processor_iface import IProcessor

class NullProcessor(IProcessor):
    """ Stub processor passthrough """

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ Returns the message and an OK status """
        return Status.OK(), message
