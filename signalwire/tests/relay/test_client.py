import asyncio
import logging
import aiohttp
from signalwire.tests.blade.blade_test_server import BladeTestServer
from signalwire.relay.client import Client
from signalwire.blade.connection import Connection
from signalwire.blade.messages.message import Message
import signalwire
import pytest
from unittest.mock import patch, MagicMock, ANY
from asynctest import CoroutineMock

logging.basicConfig(level=logging.DEBUG)

# TEST_UUIDS = ['uuid_{}'.format(i) for i in range(10000)]

def mock_blade_connect(message):
  print('mock_blade_connect')
  print(message.id)
  fut = asyncio.Future()
  json = '{"jsonrpc":"2.0","id":"' + message.id +'","result":{"session_restored":false,"sessionid":"87cf6699-7a89-4491-b732-b51144155d46","nodeid":"uuid_node","master_nodeid":"00000000-0000-0000-0000-000000000000","authorization":{"project":"project","expires_at":null,"scopes":["calling"],"signature":"random_signature"},"routes":[],"protocols":[],"subscriptions":[],"authorities":[],"authorizations":[],"accesses":[],"protocols_uncertified":["signalwire"]}}'
  msg = Message.from_json(json)
  fut.set_result(msg.result)
  return fut

def mock_signalwire_setup(message):
  print('mock_signalwire_setup')
  fut = asyncio.Future()
  json = '{"jsonrpc":"2.0","id":"' + message.id +'","result":{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"protocol":"signalwire_random_proto"}}}'
  msg = Message.from_json(json)
  fut.set_result(msg.result)
  return fut

def mock_setup_subscription(message):
  print('mock_setup_subscription')
  fut = asyncio.Future()
  json = '{"jsonrpc":"2.0","id":"' + message.id +'","result":{"protocol":"signalwire_random_proto","command":"add","subscribe_channels":["notifications"]}}'
  msg = Message.from_json(json)
  fut.set_result(msg.result)
  return fut

# @patch('signalwire.blade.messages.message.uuid4', side_effect=['mock1', 'mock2', 'mock3'])
# def test_helper_right(mock_uuid4, capsys):
#   assert mock_uuid4.called

# @patch.object(signalwire.relay.client.Connection, 'send')
# @patch('signalwire.blade.connection.Connection', mock_send)

@pytest.mark.asyncio
@patch('signalwire.blade.messages.message.uuid4', side_effect=['mock1', 'mock2', 'mock3'])
async def test_example(m):
  with patch.object(signalwire.blade.connection.Connection, 'send', return_value=CoroutineMock(return_value=asyncio.Future()), side_effect=mock_blade_connect) as send_mock:
    with patch.object(aiohttp.ClientSession, 'ws_connect', new=CoroutineMock()) as ws_connect_mock:
      client = Client(project='project', token='token')
      await client._connect()
      ws_connect_mock.assert_called_once()
      # await client.disconnect()
