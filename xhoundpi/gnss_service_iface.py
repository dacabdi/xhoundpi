""" Defines GNSS service interface/contracts """

from abc import ABC, abstractmethod

from .message import Message

class IGnssService(ABC):
    """ Interface/contract for protocol reader implementations """

    @abstractmethod
    async def read_message(self) -> Message:
        """ Read a GNSS message """

    @abstractmethod
    async def write_message(self, message: Message) -> int:
        """ Write a GNSS message """
