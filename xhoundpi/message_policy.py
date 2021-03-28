""" Policy implementations for messages """

from .message import Message
from .message_policy_iface import IMessagePolicy

class AlwaysQualifiesPolicy(IMessagePolicy):
    """
    Fixed value qualification, always true
    """

    def qualifies(self, message: Message) -> bool:
        """
        Message always qualifies
        """
        return True

class HasLocationPolicy(IMessagePolicy):
    """
    Classifies messages that have latitude and longitude props
    """

    # NOTE currently we get away with non-protocol specific
    # policy because all libraries currently in use
    # use 'lat' and 'lon' for the coordinate fields

    LAT_FIELD = 'lat'
    LON_FIELD = 'lon'

    def qualifies(self, message: Message) -> bool:
        """
        Message qualifies if it contains latitude and longitude information
        """
        return (hasattr(message.payload, 'lat',
                hasattr(message.payload, 'lon')))
