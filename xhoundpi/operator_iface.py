""" Message operators """

from abc import ABC, abstractmethod

from .message import Message

class IMessageOperator(ABC):
    """
    Interface/contract for message operators
    """

    @abstractmethod
    def operate(self, message: Message) -> Message:
        """
        Operate on the message and return the transformed version
        """
