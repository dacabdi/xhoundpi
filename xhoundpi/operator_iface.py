''' Message operators '''

from abc import ABC, abstractmethod
from typing import Tuple

from .status import Status
from .message import Message

class IMessageOperator(ABC):
    '''
    Interface/contract for message operators
    '''

    @abstractmethod
    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
