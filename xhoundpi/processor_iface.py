""" Defines GNSS service interface/contracts """

from typing import Tuple
from abc import ABC, abstractmethod

from .message import Message
from .status import Status

class IProcessor(ABC):
    """ Interface/contract for message processors """

    @abstractmethod
    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ Process a GNSS message """
