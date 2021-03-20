""" Decorators for IGnssService implementations """

from typing import Tuple

from structlog import get_logger

from .status import Status
from .gnss_service_iface import IGnssService
from .message import Message
from .monkey_patching import add_method

@add_method(IGnssService)
def with_traces(self, trace_provider):
    """ Provides decorated GNSS service with traces """
    return GnssServiceWithTraces(self, trace_provider)

@add_method(IGnssService)
def with_events(self):
    """ Provides decorated GNSS service with event logs """
    return GnssServiceWithEvents(self)

class GnssServiceWithTraces(IGnssService):
    """ IGnssService decorator for traces """

    def __init__(self, inner: IGnssService, trace_provider):
        self._inner = inner
        self._trace_provider = trace_provider

    async def read_message(self) -> Tuple[Status, Message]:
        """ Reads, classifies, and parses input from the GNSS client stream with traces """
        with self._trace_provider.start_as_current_span("read"):
            status, message = await self._inner.read_message()
            return status, message

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        """ Writes messages as byte strings to the GNSS client input with traces """
        with self._trace_provider.start_as_current_span("write"):
            status, bytes_written = await self._inner.write_message(message)
            return status, bytes_written

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_trace_provider'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)


class GnssServiceWithEvents(IGnssService):
    """ IGnssService decorator for events """

    LOGGER_NAME = 'GnssService'

    def __init__(self, inner: IGnssService):
        self._logger = get_logger(__class__.LOGGER_NAME)
        self._inner = inner

    async def read_message(self) -> Tuple[Status, Message]:
        """ Reads, classifies, and parses input from the GNSS client stream with log events """
        self._logger.info('read_start')
        status, message = await self._inner.read_message()
        self._logger.info('read_end', success=status.ok, message_id=message.message_id)
        return status, message

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        """ Writes messages as byte strings to the GNSS client input with log events """
        self._logger.info('write_start', success=True, message_id=message.message_id, bytes_written=0)
        status, bytes_written = await self._inner.write_message(message)
        self._logger.info('write_end', success=status.ok, message_id=message.message_id, bytes_written=bytes_written)
        return status, message

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_logger'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
