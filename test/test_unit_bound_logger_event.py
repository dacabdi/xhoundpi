# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import logging # pylint: disable=unused-import
import unittest
import uuid

from dataclasses import dataclass
from enum import Enum, auto

import structlog
from structlog.testing import capture_logs

from .log_utils import setup_test_event_logger

class TestEventOp(Enum):
    BeginSomeOperation = 1
    EndSomeOperation = auto()

@dataclass(order=True)
class TestEvent:
    operation: TestEventOp
    success: bool
    activity_id: uuid.UUID
    details: str = ''
    schema_ver: int = 1

@dataclass(order=True)
class LogEvent:
    message: str = ''
    schema_ver: int = 1

class Enum1(Enum):
    Enum1Value1 = 1
    Enum1Value2 = 2

class Enum2(Enum):
    Enum2Value1 = 1
    Enum2Value2 = 2

@dataclass(order=True)
class EnumsEvent:
    enum1: Enum1
    enum2: Enum2

@dataclass(order=True)
class PrimitivesEvent:
    integer: int
    string: str
    boolean: bool

def setUpModule():
    setup_test_event_logger()

class test_BoundLoggerEvent(unittest.TestCase):

    def test_mixed_event(self):
        logger = structlog.get_logger()
        event = TestEvent(
            operation=TestEventOp.BeginSomeOperation,
            success=True,
            activity_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            details='waiting for godot')
        with capture_logs() as capture:
            logger.log(logging.INFO, event)

        self.assertEqual(capture,
            [{'activity_id': '12345678-1234-5678-1234-567812345678',
            'details': 'waiting for godot',
            'event': 'TestEvent',
            'log_level': 'info',
            'operation': 1,
            'operation_name': 'BeginSomeOperation',
            'schema_ver': 1,
            'success': True}])

    def test_enums_are_valued_and_names_are_added(self):
        logger = structlog.get_logger()
        event = EnumsEvent(enum1=Enum1.Enum1Value2, enum2=Enum2.Enum2Value1)
        with capture_logs() as capture:
            logger.info(event)

        self.assertEqual(capture,
            [{'event': 'EnumsEvent',
            'log_level': 'info',
            'enum1': 2,
            'enum1_name': 'Enum1Value2',
            'enum2': 1,
            'enum2_name': 'Enum2Value1'}])

    def test_primitives_are_not_serialized(self):
        logger = structlog.get_logger()
        event = PrimitivesEvent(integer=10, string='cherry berry', boolean=False)
        with capture_logs() as capture:
            logger.info(event)

        self.assertEqual(capture,
            [{'event': 'PrimitivesEvent',
            'log_level': 'info',
            'integer': 10,
            'string': 'cherry berry',
            'boolean': False}])

    def test_empty_exception(self):
        logger = structlog.get_logger()
        event = TestEvent(
            operation=TestEventOp.BeginSomeOperation,
            success=False,
            activity_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            details='waiting for godot')
        with capture_logs() as capture:
            logger.exception(event)

        self.assertEqual(capture,
            [{'activity_id': '12345678-1234-5678-1234-567812345678',
            'details': 'waiting for godot',
            'event': 'TestEvent',
            'log_level': 'error',
            'operation': 1,
            'operation_name': 'BeginSomeOperation',
            'schema_ver': 1,
            'success': False,
            'exc_info': True}])

    def test_exception(self):
        logger = structlog.get_logger()
        event = TestEvent(
            operation=TestEventOp.EndSomeOperation,
            success=False,
            activity_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            details='waiting for godot')
        with capture_logs() as capture:
            try:
                raise RuntimeError('oops!')
            except RuntimeError: # pylint: disable=broad-except
                logger.exception(event, exc_info=True)

        self.assertEqual(capture,
            [{'activity_id': '12345678-1234-5678-1234-567812345678',
            'details': 'waiting for godot',
            'event': 'TestEvent',
            'log_level': 'error',
            'operation': 2,
            'operation_name': 'EndSomeOperation',
            'schema_ver': 1,
            'success': False,
            'exc_info': True}])
