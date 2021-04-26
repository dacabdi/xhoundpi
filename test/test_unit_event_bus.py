# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import uuid
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from xhoundpi.event_bus import Event, EventTopic
from xhoundpi.async_ext import run_sync

class test_EventTopic(unittest.TestCase):

    def test_subscriber_should_receive_published_events(self):
        sub = Mock()
        timestamp = Mock(side_effect=[
            datetime(1989, 1, 24),
            datetime(1974, 6, 12),
            datetime(1992, 1, 16)])
        topic = EventTopic("test_topic", timestamp=timestamp)
        handle = topic.subscribe(on_next=sub)

        sub.assert_not_called()
        self.assertEqual("test_topic", topic.name)
        self.assertEqual(-1, topic.offset)

        ids = [uuid.UUID('{11111111-2222-3333-4444-555555555555}'),
               uuid.UUID('{11111111-2222-3333-4444-555555555556}'),
               uuid.UUID('{11111111-2222-3333-4444-555555555557}'),]

        with patch('uuid.uuid4', side_effect=ids):
            run_sync(topic.publish("first"))
            self.assertEqual(0, topic.offset)
            sub.assert_called_once_with(Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555555}'),
                topic = "test_topic",
                timestamp = datetime(1989, 1, 24),
                offset = 0,
                payload = "first"))

            run_sync(topic.publish("second"))
            self.assertEqual(1, topic.offset)
            sub.assert_called_with(Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555556}'),
                topic = "test_topic",
                timestamp = datetime(1974, 6, 12),
                offset = 1,
                payload = "second"))

            # not called anymore after disposing the handle (self unsubscribing)
            handle.dispose()

            run_sync(topic.publish("third"))
            sub.assert_called_with(Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555556}'),
                topic = "test_topic",
                timestamp = datetime(1974, 6, 12),
                offset = 1,
                payload = "second"))

    def test_events_should_be_broadcasted_to_all_subscribers(self): # pylint: disable=no-self-use
        sub0 = Mock()
        sub1 = Mock()
        sub2 = Mock()

        timestamp = Mock(side_effect=[
            datetime(1989, 1, 24),
            datetime(1974, 6, 12),
            datetime(1992, 1, 16)])
        topic = EventTopic("test_topic", timestamp=timestamp)
        handle0 = topic.subscribe(on_next=sub0)
        handle1 = topic.subscribe(on_next=sub1)
        handle2 = topic.subscribe(on_next=sub2)

        sub0.assert_not_called()
        sub1.assert_not_called()
        sub2.assert_not_called()

        self.assertEqual("test_topic", topic.name)
        self.assertEqual(-1, topic.offset)

        ids = [uuid.UUID('{11111111-2222-3333-4444-555555555555}'),
               uuid.UUID('{11111111-2222-3333-4444-555555555556}'),
               uuid.UUID('{11111111-2222-3333-4444-555555555557}'),]

        with patch('uuid.uuid4', side_effect=ids):
            run_sync(topic.publish("first"))
            self.assertEqual(0, topic.offset)
            expected_event0 = Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555555}'),
                topic = "test_topic",
                timestamp = datetime(1989, 1, 24),
                offset = 0,
                payload = "first")
            sub0.assert_called_once_with(expected_event0)
            sub1.assert_called_once_with(expected_event0)
            sub2.assert_called_once_with(expected_event0)

            run_sync(topic.publish("second"))
            self.assertEqual(1, topic.offset)
            expected_event1 = Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555556}'),
                topic = "test_topic",
                timestamp = datetime(1974, 6, 12),
                offset = 1,
                payload = "second")
            sub0.assert_called_with(expected_event1)
            sub1.assert_called_with(expected_event1)
            sub2.assert_called_with(expected_event1)

            handle0.dispose()
            handle1.dispose()

            run_sync(topic.publish("third"))
            self.assertEqual(2, topic.offset)
            sub0.assert_called_with(expected_event1)
            sub1.assert_called_with(expected_event1)
            sub2.assert_called_with(Event(
                id = uuid.UUID('{11111111-2222-3333-4444-555555555557}'),
                topic = "test_topic",
                timestamp = datetime(1992, 1, 16),
                offset = 2,
                payload = "third"))

            handle2.dispose()

    def test_exception(self): # pylint: disable=no-self-use
        on_next = Mock()
        on_error = Mock()
        timestamp = Mock(side_effect=[datetime(1989, 1, 24)])
        topic = EventTopic("test_topic", timestamp=timestamp)
        _ = topic.subscribe(on_next=on_next, on_error=on_error)

        on_error.assert_not_called()
        with patch('asyncio.queues.Queue.get', side_effect=Exception('Oops!')):
            run_sync(topic.publish("first"))

        on_next.assert_not_called()
        self.assertEqual(["call(Exception('Oops!'))"],
            [str(arg) for arg in on_error.call_args_list])
