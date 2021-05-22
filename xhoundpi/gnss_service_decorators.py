''' Decorators for IGnssService implementations '''

import logging
import uuid

from typing import Tuple

from .proto_class import ProtocolClass
from .events.common import ZERO_UUID
from .events.gnss_service_action import GnssServiceAction, GnssServiceOp
from .status import Status
from .gnss_service_iface import IGnssService
from .message import Message
from .monkey_patching import add_method
from .metric import LatencyMetric, SuccessCounterMetric

@add_method(IGnssService)
def with_traces(self, trace_provider):
    ''' Provides decorated GNSS service with traces '''
    return GnssServiceWithTraces(self, trace_provider)

@add_method(IGnssService)
def with_events(self, logger):
    ''' Provides decorated GNSS service with event logs '''
    return GnssServiceWithEvents(self, logger)

@add_method(IGnssService)
def with_metrics(self,
    rcounter: SuccessCounterMetric,
    wcounter: SuccessCounterMetric,
    rlatency: LatencyMetric,
    wlatency: LatencyMetric):
    ''' Provides decorated GNSS service with metrics '''
    return GnssServiceWithMetrics(self, rcounter, wcounter, rlatency, wlatency)

class GnssServiceWithTraces(IGnssService):
    ''' IGnssService decorator for traces '''

    def __init__(self, inner: IGnssService, trace_provider):
        self._inner = inner
        self._trace_provider = trace_provider

    async def read_message(self) -> Tuple[Status, Message]:
        ''' Reads, classifies, and parses input from the GNSS client stream with traces '''
        with self._trace_provider.start_as_current_span("read"):
            status, message = await self._inner.read_message()
            return status, message

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        ''' Writes messages as byte strings to the GNSS client input with traces '''
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
    ''' IGnssService decorator for events '''

    def __init__(self, inner: IGnssService, logger):
        self._logger = logger
        self._inner = inner

    async def read_message(self) -> Tuple[Status, Message]:
        ''' Reads, classifies, and parses input from the GNSS client stream with log events '''
        activity_id = uuid.uuid4()
        self._log_read_start(activity_id)
        status, message = await self._inner.read_message()
        self._log_read_end(activity_id, status, message)
        return status, message

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        ''' Writes messages as byte strings to the GNSS client input with log events '''
        activity_id = uuid.uuid4()
        self._log_write_start(activity_id, message)
        status, cbytes = await self._inner.write_message(message)
        self._log_write_end(activity_id, status, message, cbytes)
        return status, cbytes

    def _log_read_start(self, activity_id: uuid.UUID):
        self._logger.info(GnssServiceAction(
            opcode=GnssServiceOp.BeginRead,
            success=True,
            activity_id=activity_id,
            details='',
            message_id=ZERO_UUID,
            protocol=ProtocolClass.NONE))

    def _log_read_end(self, activity_id: uuid.UUID, status: Status, message: Message):
        if status.ok:
            self._logger.info(GnssServiceAction(
                opcode=GnssServiceOp.EndRead,
                success=True,
                activity_id=activity_id,
                details='',
                message_id=message.message_id,
                protocol=message.proto))
        else:
            self._logger.exception(GnssServiceAction(
                opcode=GnssServiceOp.EndRead,
                success=False,
                activity_id=activity_id,
                details=str(status.error),
                message_id=ZERO_UUID,
                protocol=ProtocolClass.NONE))

    def _log_write_start(self, activity_id: uuid.UUID, message):
        self._logger.info(GnssServiceAction(
            opcode=GnssServiceOp.BeginWrite,
            success=True,
            activity_id=activity_id,
            details='',
            message_id=message.message_id,
            protocol=message.proto))

    def _log_write_end(self, activity_id: uuid.UUID, status: Status, message: Message, cbytes: int):
        if status.ok:
            level = logging.INFO
            success = True
            details = f'{cbytes} bytes'
        else:
            level = logging.ERROR
            success = False
            details = str(status.error)
        self._logger.log(
            level,
            GnssServiceAction(
                opcode=GnssServiceOp.EndWrite,
                success=success,
                activity_id=activity_id,
                details=details,
                message_id=message.message_id,
                protocol=message.proto))

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

class GnssServiceWithMetrics(IGnssService):
    ''' IGnssService decorator for metrics '''

    # pylint: disable=too-many-arguments
    def __init__(self, inner: IGnssService,
        rcounter: SuccessCounterMetric,
        wcounter: SuccessCounterMetric,
        rlatency: LatencyMetric,
        wlatency: LatencyMetric):
        self._inner = inner
        self._rcounter = rcounter
        self._wcounter = wcounter
        self._rlatency = rlatency
        self._wlatency = wlatency

    async def read_message(self) -> Tuple[Status, Message]:
        ''' Reads, classifies, and parses input from the GNSS
        client stream with latency and success metrics '''
        with self._rlatency:
            status, message = await self._inner.read_message()
        self._rcounter.increase(is_success=status.ok)
        return status, message

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        ''' Writes messages as byte strings to the GNSS
        client stream with latency and success metrics '''
        with self._wlatency:
            status, cbytes = await self._inner.write_message(message)
        self._wcounter.increase(is_success=status.ok)
        return status, cbytes

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_rcounter', '_wcounter', '_rlatency', '_wlatency'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
