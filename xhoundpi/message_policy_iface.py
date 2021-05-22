''' Policy qualification for messages '''

from abc import ABC, abstractmethod

from .message import Message

class IMessagePolicy(ABC):
    '''
    Message policy contract/interface
    '''

    @abstractmethod
    def qualifies(self, message: Message) -> bool:
        '''
        Qualifies affirmatevily or negatively the provided message.
        This abstraction can be used to compositively make decisions
        for messages.
        '''
