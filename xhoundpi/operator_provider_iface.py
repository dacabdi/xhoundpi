''' Contract for message operator providers '''

from abc import ABC, abstractmethod

from .message import Message
from .operator_iface import IMessageOperator

class IMessageOperatorProvider(ABC):
    '''
    Interface/contract for message operator provider
    '''

    @abstractmethod
    def get_operator(self, message: Message) -> IMessageOperator:
        '''
        Returns an operator for the message
        '''
