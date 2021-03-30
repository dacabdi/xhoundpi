# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import unittest
import uuid

from unittest.mock import Mock

from asynctest import CoroutineMock

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.status import Status
from xhoundpi.async_ext import run_sync
from xhoundpi.processor import (NullProcessor,
                               GenericProcessor,
                               CompositeProcessor)

class test_NullProcessor(unittest.TestCase):

    def test_process_should_passthrough(self):
        processor = NullProcessor()
        message = Message(
            message_id=uuid.UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
            proto=ProtocolClass.NONE,
            payload=None)

        status, transformed_msg = run_sync(processor.process(message))

        self.assertEqual(status, Status.OK())
        self.assertEqual(transformed_msg, message)

class test_GenericProcessor(unittest.TestCase):

    def test_process(self):
        msg = Message(uuid.UUID('{12345678-1234-5678-1234-567812345678}'), None, None)
        policy = Mock()
        policy.qualifies = Mock(return_value=True)
        policy_provider = Mock()
        policy_provider.get_policy = Mock(return_value=policy)
        operator = Mock()
        operator.operate = Mock(return_value=(Status.OK(), 'new message'))
        operator_provider = Mock()
        operator_provider.get_operator = Mock(return_value=operator)
        processor = GenericProcessor(
            name='Processor1',
            policy_provider=policy_provider,
            operator_provider=operator_provider)

        result = run_sync(processor.process(msg))

        self.assertEqual((Status.OK(metadata={'qualified':True}), 'new message'), result)
        policy_provider.get_policy.assert_called_once_with(msg)
        policy.qualifies.assert_called_once_with(msg)
        operator_provider.get_operator.assert_called_once_with(msg)
        operator.operate.assert_called_once_with(msg)
        self.assertEqual(processor._name, 'Processor1') # pylint: disable=protected-access

    def test_policy_not_qualifies_process(self):
        msg = Message(uuid.UUID('{12345678-1234-5678-1234-567812345678}'), None, None)
        policy = Mock()
        policy.qualifies = Mock(return_value=False)
        policy_provider = Mock()
        policy_provider.get_policy = Mock(return_value=policy)
        operator = Mock()
        operator.operate = Mock(return_value=(Status.OK(), 'new message'))
        operator_provider = Mock()
        operator_provider.get_operator = Mock(return_value=operator)
        processor = GenericProcessor(
            name='Processor1',
            policy_provider=policy_provider,
            operator_provider=operator_provider)

        result = run_sync(processor.process(msg))

        self.assertEqual((Status.OK(metadata={'qualified':False}), msg), result)
        policy_provider.get_policy.assert_called_once_with(msg)
        policy.qualifies.assert_called_once_with(msg)
        operator_provider.get_operator.assert_not_called()
        operator.operate.assert_not_called()
        self.assertEqual(processor._name, 'Processor1') # pylint: disable=protected-access

    def test_error_process_returns_original_msg(self):
        msg = Message(uuid.UUID('{12345678-1234-5678-1234-567812345678}'), None, None)
        policy = Mock()
        policy.qualifies = Mock(return_value=False)
        policy_provider = Mock()
        policy_provider.get_policy = Mock(side_effect=Exception('Error!'))
        operator = Mock()
        operator.operate = Mock(return_value=(Status.OK(), 'new message'))
        operator_provider = Mock()
        operator_provider.get_operator = Mock(return_value=operator)
        processor = GenericProcessor(
            name='Processor1',
            policy_provider=policy_provider,
            operator_provider=operator_provider)

        result = run_sync(processor.process(msg))

        self.assertEqual((Status(Exception('Error!'),
            metadata={'qualified':False}), msg), result)
        policy_provider.get_policy.assert_called_once_with(msg)
        policy.qualifies.assert_not_called()
        operator_provider.get_operator.assert_not_called()
        operator.operate.assert_not_called()
        self.assertEqual(processor._name, 'Processor1') # pylint: disable=protected-access

    def test_error_process_returns_original_msg2(self):
        msg = Message(uuid.UUID('{12345678-1234-5678-1234-567812345678}'), None, None)
        policy = Mock()
        policy.qualifies = Mock(return_value=True)
        policy_provider = Mock()
        policy_provider.get_policy = Mock(return_value=policy)
        operator = Mock()
        operator.operate = Mock(return_value=(Status.OK(), 'new message'))
        operator_provider = Mock()
        operator_provider.get_operator = Mock(side_effect=Exception('Failed!'))
        processor = GenericProcessor(
            name='Processor1',
            policy_provider=policy_provider,
            operator_provider=operator_provider)

        result = run_sync(processor.process(msg))

        self.assertEqual((Status(Exception('Failed!'),
            metadata={'qualified':True}), msg), result)
        policy_provider.get_policy.assert_called_once_with(msg)
        policy.qualifies.assert_called_once_with(msg)
        operator_provider.get_operator.assert_called_once_with(msg)
        operator.operate.assert_not_called()
        self.assertEqual(processor._name, 'Processor1') # pylint: disable=protected-access

class test_CompositeProcessor(unittest.TestCase):

    def test_process(self):
        proc1 = Mock()
        proc1.process = CoroutineMock(return_value=(Status.OK(), 'msg1'))
        proc2 = Mock()
        proc2.process = CoroutineMock(return_value=(Status.OK(), 'msg2'))
        proc3 = Mock()
        proc3.process = CoroutineMock(return_value=(Status.OK(), 'msg3'))
        processor = CompositeProcessor([proc1, proc2, proc3])

        result = run_sync(processor.process('msg0'))

        proc1.process.assert_awaited_once_with('msg0')
        proc2.process.assert_awaited_once_with('msg1')
        proc3.process.assert_awaited_once_with('msg2')
        self.assertEqual((Status.OK(), 'msg3'), result)

    def test_process_stop_and_return_original_on_exception(self):
        proc1 = Mock()
        proc1.process = CoroutineMock(return_value=(Status.OK(), 'msg1'))
        proc2 = Mock()
        proc2.process = CoroutineMock(side_effect=Exception('Error!'))
        proc3 = Mock()
        proc3.process = CoroutineMock(return_value=(Status.OK(), 'msg3'))

        processor = CompositeProcessor([proc1, proc2, proc3])

        result = run_sync(processor.process('msg0'))

        proc1.process.assert_awaited_once_with('msg0')
        proc2.process.assert_awaited_once_with('msg1')
        proc3.process.assert_not_awaited()
        self.assertEqual((Status(Exception('Error!')), 'msg0'), result)

    def test_process_stop_and_return_original_on_status_not_ok(self):
        proc1 = Mock()
        proc1.process = CoroutineMock(return_value=(Status.OK(), 'msg1'))
        proc2 = Mock()
        proc2.process = CoroutineMock(return_value=(Status(Exception('Error!')), 'msg1'))
        proc3 = Mock()
        proc3.process = CoroutineMock(return_value=(Status.OK(), 'msg3'))

        processor = CompositeProcessor([proc1, proc2, proc3])

        result = run_sync(processor.process('msg0'))

        proc1.process.assert_awaited_once_with('msg0')
        proc2.process.assert_awaited_once_with('msg1')
        proc3.process.assert_not_awaited()
        self.assertEqual((Status(Exception('Error!')), 'msg0'), result)
