""" Decorators for IGnssService implementations """

from .gnss_service_iface import IGnssService
from .message import Message
from .monkey_patching import add_method

@add_method(IGnssService)
def with_traces(self, trace_provider):
    """ Provides decorated GNSS service with traces """
    return GnssServiceWithTraces(self, trace_provider)

class GnssServiceWithTraces(IGnssService):
    """ IGnssService decorator for traces """

    def __init__(self, inner: IGnssService, trace_provider):
        self._inner = inner
        self._trace_provider = trace_provider

    async def read_message(self) -> Message:
        """ Reads, classifies, and parses input from the GNSS client stream with traces """
        with self._trace_provider.start_as_current_span("read"):
            result = await self._inner.read_message()
            return result

    async def write_message(self, message: Message) -> int:
        """ Writes messages as byte strings to the GNSS client input with traces """
        with self._trace_provider.start_as_current_span("write"):
            result = await self._inner.write_message(message)
            return result

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
