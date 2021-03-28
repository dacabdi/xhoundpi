""" Policy provider implementations for messages """

from .message import Message
from .message_policy_iface import IMessagePolicy
from .message_policy_provider_iface import IMessagePolicyProvider

class ProtocolPolicyProvider(IMessagePolicyProvider):
    """
    Message policy provider based on protocol
    """

    def __init__(self, mapping: dict):
        self.__mapping = mapping

    def get_policy(self, message: Message) -> IMessagePolicy:
        """
        Returns the applicable policy for
        the message based on the protocol
        """
        return self.__mapping[message.proto]

class OnePolicyProvider(IMessagePolicyProvider):
    """
    Message policy provider that always provides the same policy
    """

    def __init__(self, policy: IMessagePolicy):
        self.__policy = policy

    def get_policy(self, message: Message) -> IMessagePolicy:
        """
        Returns the configured policy
        """
        return self.__policy
