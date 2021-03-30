""" Message policy provider contract/interface """

from abc import ABC, abstractmethod

from .message_policy_iface import IMessagePolicy
from .message import Message

class IMessagePolicyProvider(ABC):
    """
    Message policy provider contract/interface
    """

    @abstractmethod
    def get_policy(self, message: Message) -> IMessagePolicy:
        """
        Returns the applicable policy for the message
        """
