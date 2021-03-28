# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from  unittest.mock import Mock

from xhoundpi.message import Message
from xhoundpi.message_policy_iface import IMessagePolicy
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message_policy_provider import (MessageProtocolPolicyProvider,
                                             OnePolicyProvider,)

class test_MessageProtocolPolicyProvider(unittest.TestCase):

    def returns_policy_per_protocol(self):
        ubx_policy = Mock(IMessagePolicy)
        nmea_policy = Mock(IMessagePolicy)
        provider = MessageProtocolPolicyProvider({
            ProtocolClass.NMEA: nmea_policy,
            ProtocolClass.UBX: ubx_policy,
        })
        self.assertEqual(ubx_policy, provider.get_policy(Message(None, ProtocolClass.NMEA, None)))
        self.assertEqual(ubx_policy, provider.get_policy(Message(None, ProtocolClass.UBX, None)))

    def returns_raises_if_no_policy(self):
        provider = MessageProtocolPolicyProvider({})
        with self.assertRaises(KeyError) as context:
            provider.get_policy(Message(None, ProtocolClass.NMEA, None))
        print(str(context.exception))

class test_OnePolicyProvider(unittest.TestCase):

    def returns_same_policy_always(self):
        policy = Mock(IMessagePolicy)
        provider = OnePolicyProvider(policy)
        self.assertEqual(policy, provider.get_policy(Message(None, ProtocolClass.NMEA, None)))
        self.assertEqual(policy, provider.get_policy(Message(None, ProtocolClass.UBX, None)))
