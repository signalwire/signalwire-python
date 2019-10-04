import asyncio
import pytest
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.execute import Execute
from signalwire.relay.client import Client
from unittest.mock import Mock
from signalwire.tests import AsyncMock, MockedConnection

@pytest.mark.asyncio
async def test_connect(relay_client_to_connect):
  ready_callback = Mock()
  relay_client_to_connect.on('ready', ready_callback)
  await relay_client_to_connect._connect()

  pending_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
  await asyncio.gather(*pending_tasks)

  assert relay_client_to_connect.session_id == '87cf6699-7a89-4491-b732-b51144155d46'
  assert relay_client_to_connect.protocol == 'signalwire_random_proto'
  ready_callback.assert_called_once()

@pytest.mark.asyncio
async def test_blade_disconnect(relay_client_to_connect):
  assert relay_client_to_connect._idle == False
  blade_disconnect = Message.from_json('{"id":"378d7dea-e581-4305-a7e7-d29173797f32","jsonrpc":"2.0","method":"blade.disconnect","params":{}}')
  relay_client_to_connect.message_handler(blade_disconnect)
  assert relay_client_to_connect._idle == True

  async def _reconnect():
    assert relay_client_to_connect._executeQueue.qsize() == 1
    relay_client_to_connect.connection.responses.append('{"jsonrpc":"2.0","id":"uuid","result":{"test":"done"}}')
    await relay_client_to_connect._connect()

  asyncio.create_task(_reconnect())
  message = Execute({ 'protocol': 'fake', 'method': 'testing', 'params': {} })
  result = await relay_client_to_connect.execute(message)

  assert relay_client_to_connect._idle == False
  assert relay_client_to_connect._executeQueue.qsize() == 0
  assert result['test'] == 'done'
