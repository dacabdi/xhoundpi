''' Defines GNSS service interface/contracts '''

from typing import Tuple
from abc import ABC, abstractmethod

from .message import Message
from .status import Status

class IGnssService(ABC):
    ''' Interface/contract for protocol reader implementations '''

    @abstractmethod
    async def read_message(self) -> Tuple[Status, Message]:
        ''' Read a GNSS message '''

    @abstractmethod
    async def write_message(self, message: Message) -> Tuple[Status, int]:
        ''' Write a GNSS message '''
