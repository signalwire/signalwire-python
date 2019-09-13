import asyncio
import logging
import pytest
from signalwire.relay.client import Client
from unittest.mock import Mock
from signalwire.tests import AsyncMock, MockedConnection

logging.basicConfig(level=logging.DEBUG)

@pytest.mark.asyncio
async def test_example():
  responses = [
    '{"jsonrpc":"2.0","id":"uuid","result":{"session_restored":false,"sessionid":"87cf6699-7a89-4491-b732-b51144155d46","nodeid":"uuid_node","master_nodeid":"00000000-0000-0000-0000-000000000000","authorization":{"project":"project","expires_at":null,"scopes":["calling"],"signature":"random_signature"},"routes":[],"protocols":[],"subscriptions":[],"authorities":[],"authorizations":[],"accesses":[],"protocols_uncertified":["signalwire"]}}',
    '{"jsonrpc":"2.0","id":"uuid","result":{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"protocol":"signalwire_random_proto"}}}',
    '{"jsonrpc":"2.0","id":"uuid","result":{"protocol":"signalwire_random_proto","command":"add","subscribe_channels":["notifications"]}}'
  ]
  client = Client(project='project', token='token', connection=MockedConnection)
  client.connection.responses = responses
  ready_callback = Mock()
  client.on('ready', ready_callback)
  await client._connect()

  pending_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
  # should be just 'on_socket_open' task
  assert 1 == len(pending_tasks)
  # await on_socket_open to finish...
  await asyncio.gather(*pending_tasks)
  assert client.session_id == '87cf6699-7a89-4491-b732-b51144155d46'
  assert client.protocol == 'signalwire_random_proto'
  ready_callback.assert_called_once()
