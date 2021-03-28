""" Interface/contract for message editors """

from abc import ABC, abstractmethod
from typing import Dict, Tuple

from .status import Status
from .message import Message

class IMessageEditor(ABC):
    """
    Interface/contract for message editors
    """

    @abstractmethod
    def set_fields(self, message: Message, fields: Dict) -> Tuple[Status, Message]:
        """
        Set the message payload fields using a list of substitutions
        """
