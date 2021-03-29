""" Defines GNSS service interface/contracts """

from typing import List, Tuple

from .message import Message
from .status import Status
from .processor_iface import IProcessor
from .operator_provider_iface import IMessageOperatorProvider
from .message_policy_provider_iface import IMessagePolicyProvider

class NullProcessor(IProcessor):
    """ Stub processor passthrough """

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ Returns the message and an OK status """
        return Status.OK(), message

class GenericProcessor(IProcessor):
    """ Applies a correction to the message based on qualification
    policies and operation providers set during initialization """

    def __init__(self,
        name: str,
        policy_provider: IMessagePolicyProvider,
        operator_provider: IMessageOperatorProvider):
        self._name = name
        self.__policy_provider = policy_provider
        self.__operator_provider = operator_provider

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ If the policy provided by the policy provider for the message
        indicates that the message must be processed, the operation is obtained
        from the operation provider and applied to the message. If failed,
        will return the original message and the status """
        # TODO clean up this logic
        metadata = {'qualified' : False}
        try:
            policy = self.__policy_provider.get_policy(message)
            if policy.qualifies(message):
                metadata['qualified'] = True
                operator = self.__operator_provider.get_operator(message)
                status, result = operator.operate(message)
                if status.ok:
                    return Status.OK(metadata=metadata), result
                return Status(result.error, metadata=metadata), message
            return Status.OK(metadata=metadata), message
        except Exception as ex: # pylint: disable=broad-except
            return Status(ex, metadata=metadata), message

class CompositeProcessor(IProcessor):
    """ Applies a series of processes in sequence """

    def __init__(self, operators: List[IProcessor]):
        self.__processors = operators

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """
        Runs all composed operations over the message.
        If an operation fails, returns original message
        and status code.
        """
        proccessed = message
        for processor in self.__processors:
            try:
                status, proccessed = await processor.process(proccessed)
                if not status.ok:
                    return status, message
            except Exception as ex: # pylint: disable=broad-except
                return Status(ex), message
        return Status.OK(), proccessed
