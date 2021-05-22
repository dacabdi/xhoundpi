''' Decorators for IGnssClient implementations '''

from .metric import ValueMetric
from .gnss_client import IGnssClient
from .monkey_patching import add_method

@add_method(IGnssClient)
def with_metrics(self,
    cbytes_read: ValueMetric,
    cbytes_written: ValueMetric):
    ''' Provides decorated GNSS client with metrics '''
    return GnssClientWithMetrics(self, cbytes_read, cbytes_written)

class GnssClientWithMetrics(IGnssClient):
    ''' IGnssClient decorator for metrics '''

    def __init__(self,
        inner: IGnssClient,
        cbytes_read: ValueMetric,
        cbytes_written: ValueMetric):
        self._inner = inner
        self._cbytes_read = cbytes_read
        self._cbytes_written = cbytes_written

    def read(self, size) -> bytes:
        ''' Read n bytes from GNSS device transport and count bytes '''
        data = self._inner.read(size)
        self._cbytes_read.add(len(data))
        return data

    def write(self, data: bytes) -> int:
        ''' Write bytes to GNSS device transport and count bytes '''
        cbytes = self._inner.write(data)
        self._cbytes_written.add(cbytes)
        return cbytes

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_cbytes_read', '_cbytes_written'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
