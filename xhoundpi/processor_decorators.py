""" Decorators for IProcessor implementations """

import logging
import uuid

from typing import Tuple

from .processor_iface import IProcessor
from .events import (ProcessorAction,
                    ProcessorOp)
from .status import Status
from .message import Message
from .monkey_patching import add_method
from .metric import (LatencyMetric,
                    SuccessCounterMetric)

@add_method(IProcessor)
def with_events(self, logger):
    """ Provides decorated processors with event logs """
    return ProcessorWithEvents(self, logger)

@add_method(IProcessor)
def with_metrics(self,
    counter: SuccessCounterMetric,
    latency: LatencyMetric,):
    """ Provides decorated processors with metrics """
    return ProcessorWithMetrics(self, counter, latency)

class ProcessorWithEvents(IProcessor):
    """ IProcessor decorator for event logs """

    def __init__(self, inner: IProcessor, trace_provider):
        self._name = inner._name if hasattr(inner, '_name') else inner.__class__.__name__
        self._inner = inner
        self._logger = trace_provider

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ Process GNSS message with logs """
        activity_id = uuid.uuid4()
        self._log_start(message, activity_id)
        status, message = await self._inner.process(message)
        self._log_end(status, message, activity_id)
        return status, message

    def _log_start(self, message: Message, activity_id: uuid.UUID):
        self._logger.info(ProcessorAction(
            opcode=ProcessorOp.BeginProcess,
            success=True,
            processor_id=self._name,
            activity_id=activity_id,
            message_id=message.message_id,
            protocol=message.proto,))

    def _log_end(self, status: Status, message: Message, activity_id: uuid.UUID):
        if status.ok:
            level = logging.INFO
            success = True
            details = ''
        else:
            level = logging.ERROR
            success = False
            details = status.error
        self._logger.log(level, ProcessorAction(
            opcode=ProcessorOp.EndProcess,
            success=success,
            processor_id=self._name,
            activity_id=activity_id,
            message_id=message.message_id,
            protocol=message.proto,
            details=details))

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_logger', '_name'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)

class ProcessorWithMetrics(IProcessor):
    """ IProcessor decorator for event logs """

    def __init__(self,
        inner: IProcessor,
        counter: SuccessCounterMetric,
        latency: LatencyMetric,):
        self.__class__.__name__ = inner.__class__.__name__
        self._inner = inner
        self._counter = counter
        self._latency = latency

    async def process(self, message: Message) -> Tuple[Status, Message]:
        """ Process GNSS message with metrics """
        with self._latency:
            status, message = await self._inner.process(message)
        self._counter.increase(is_success=status.ok)
        return status, message

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_counter', '_latency'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
