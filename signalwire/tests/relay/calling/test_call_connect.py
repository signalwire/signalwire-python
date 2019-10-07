import asyncio
import json
import pytest
from signalwire.relay.calling import Call

async def _fire(calling, notification):
  calling.notification_handler(notification)

@pytest.fixture()
def relay_call(relay_calling):
  params = json.loads('{"call_state":"created","context":"office","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"direction":"inbound","call_id":"call-id","node_id":"node-id","tag":"call-tag"}')
  return Call(calling=relay_calling, **params)

@pytest.mark.asyncio
async def test_connect_in_series_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.connect(
    { 'to_number': '+12029999990', 'timeout': 30 },
    { 'to_number': '+12029999991' }
  )
  assert result.successful
  assert result.call == relay_call.peer
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"call_id":"call-id","node_id":"node-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}]]}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_in_parallel_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.connect(
    [
      { 'to_number': '+12029999990', 'timeout': 30 },
    ],
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ]
  )
  assert result.successful
  assert result.call == relay_call.peer
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"call_id":"call-id","node_id":"node-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}]]}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_series_and_parallel_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.connect(
    { 'to_number': '+12029999990', 'timeout': 30 },
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ],
    { 'to_number': '+12029999993', 'from_number': '+13029999999' }
  )
  assert result.successful
  assert result.call == relay_call.peer
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"call_id":"call-id","node_id":"node-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}],[{"type":"phone","params":{"from_number":"+13029999999","to_number":"+12029999993"}}]]}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_rejection(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"disconnected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.connect({ 'to_number': '+12029999990', 'timeout': 30 })
  assert not result.successful
  assert result.call is None
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"call_id":"call-id","node_id":"node-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}]]}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.connect()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
