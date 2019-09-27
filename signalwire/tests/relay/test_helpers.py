import json
import pytest
from signalwire.relay.client import Client
from signalwire.relay.helpers import setup_protocol, receive_contexts
from signalwire.tests import AsyncMock, MockedConnection

@pytest.mark.asyncio
async def test_setup_protocol():
  client = Client(project='project', token='token', connection=MockedConnection)
  responses = [
    json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"protocol":"signalwire-proto-test"}}'),
    json.loads('{"protocol":"signalwire-proto-test","command":"add","subscribe_channels":["notifications"]}')
  ]
  client.execute = AsyncMock(side_effect=responses)
  new_protocol = await setup_protocol(client)

  assert new_protocol == 'signalwire-proto-test'
  assert client.execute.mock.call_count == 2
  setup, subscription = client.execute.mock.call_args_list
  assert setup[0][0].params == {'protocol': 'signalwire', 'method': 'setup', 'params': {}}
  assert subscription[0][0].params == {'command': 'add', 'protocol': 'signalwire-proto-test', 'channels': ['notifications']}


@pytest.mark.asyncio
async def test_receive_contexts():
  client = Client(project='project', token='token', connection=MockedConnection)
  client.protocol = 'signalwire-proto-test'
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"code":"200","message":"Receiving all inbound related to the requested relay contexts and available scopes"}}')
  client.execute = AsyncMock(return_value=response)
  await receive_contexts(client, ['default'])

  msg = client.execute.mock.call_args[0][0]
  assert msg.params.pop('protocol') == 'signalwire-proto-test'
  assert msg.params.pop('method') == 'signalwire.receive'
  assert msg.params.pop('params') == {'contexts': ['default']}
  assert client.contexts == ['default']
  client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_receive_contexts_already_present():
  client = Client(project='project', token='token', connection=MockedConnection)
  client.contexts = ['already_there']
  client.execute = AsyncMock()
  await receive_contexts(client, ['already_there'])
  assert client.contexts == ['already_there']
  client.execute.mock.assert_not_called()


@pytest.mark.asyncio
async def test_receive_contexts_with_mixed_contexts():
  client = Client(project='project', token='token', connection=MockedConnection)
  client.protocol = 'signalwire-proto-test'
  client.contexts = ['already_there']
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"code":"200","message":"Receiving all inbound related to the requested relay contexts and available scopes"}}')
  client.execute = AsyncMock(return_value=response)
  await receive_contexts(client, ['another_one'])

  msg = client.execute.mock.call_args[0][0]
  assert msg.params.pop('params') == {'contexts': ['another_one']}
  client.contexts.sort()
  assert client.contexts == ['already_there', 'another_one']
  client.execute.mock.assert_called_once()
