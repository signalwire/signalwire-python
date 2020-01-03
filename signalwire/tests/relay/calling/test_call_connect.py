import asyncio
import json
import pytest
from signalwire.blade.messages.message import JSONRPCEncoder
from signalwire.relay.calling.devices import Device
from unittest.mock import Mock

async def _fire(calling, notification):
  calling.notification_handler(notification)

@pytest.fixture()
async def relay_call_active(relay_call):
  answered_event = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"end_reason":"noAnswer","call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call.calling, answered_event)
  return relay_call

def test_connect_events(relay_call):
  mock = Mock()
  relay_call.on('connect.stateChange', mock)
  relay_call.on('connect.connected', mock)
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_connect_in_series_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 },
    { 'to_number': '+12029999991' }
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert result.successful
  assert result.call == relay_call_active.peer
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_in_series_with_ringback_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 },
    { 'to_number': '+12029999991' }
  ]
  ringback = [
    { 'type': 'audio', 'url': 'audio.mp3' },
    { 'type': 'ringtone', 'name': 'us' }
  ]
  result = await relay_call_active.connect(device_list=devices, ringback_list=ringback)
  assert result.successful
  assert result.call == relay_call_active.peer
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}]],"ringback":[{"type":"audio","params":{"url":"audio.mp3"}},{"type":"ringtone","params":{"name":"us"}}]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_in_parallel_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    [
      { 'to_number': '+12029999990', 'timeout': 30 },
    ],
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ]
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert result.successful
  assert result.call == relay_call_active.peer
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_in_parallel_with_ringback_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ]
  ]
  ringback = [
    { 'type': 'audio', 'url': 'audio.mp3' },
    { 'type': 'ringtone', 'name': 'us' }
  ]
  result = await relay_call_active.connect(device_list=devices, ringback_list=ringback)
  assert result.successful
  assert result.call == relay_call_active.peer
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}]],"ringback":[{"type":"audio","params":{"url":"audio.mp3"}},{"type":"ringtone","params":{"name":"us"}}]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_series_and_parallel_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 },
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ],
    { 'to_number': '+12029999993', 'from_number': '+13029999999' }
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert result.successful
  assert result.call == relay_call_active.peer
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}],[{"type":"phone","params":{"from_number":"+13029999999","to_number":"+12029999993"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_disconnected_event(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"disconnected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert not result.successful
  assert result.call is None
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_failed_event(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"failed","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call_active.calling, payload))
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert not result.successful
  assert result.call is None
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_failure(fail_response, relay_call_active):
  relay_call_active.calling.client.execute = fail_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  result = await relay_call_active.connect(device_list=devices)
  assert not result.successful
  relay_call_active.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_async_in_series_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 },
    { 'to_number': '+12029999991' }
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert not action.completed
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call_active.calling, payload)
  assert action.completed
  assert action.result.call == relay_call_active.peer

@pytest.mark.asyncio
async def test_connect_async_in_parallel_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  devices = [
    [
      { 'to_number': '+12029999990', 'timeout': 30 },
    ],
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ]
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert not action.completed
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call_active.calling, payload)
  assert action.completed
  assert action.result.call == relay_call_active.peer

@pytest.mark.asyncio
async def test_connect_async_series_and_parallel_with_success(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 },
    [
      { 'to_number': '+12029999991', 'timeout': 20 },
      { 'to_number': '+12029999992' }
    ],
    { 'to_number': '+12029999993', 'from_number': '+13029999999' }
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert not action.completed
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}],[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991","timeout":20}},{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999992"}}],[{"type":"phone","params":{"from_number":"+13029999999","to_number":"+12029999993"}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call_active.calling, payload)
  assert action.completed
  assert action.result.call == relay_call_active.peer

@pytest.mark.asyncio
async def test_connect_async_with_disconnected_event(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert not action.completed
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"disconnected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call_active.calling, payload)
  assert action.completed
  assert action.result.call is None

@pytest.mark.asyncio
async def test_connect_async_with_failed_event(success_response, relay_call_active):
  relay_call_active.calling.client.execute = success_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert not action.completed
  msg = relay_call_active.calling.client.execute.mock.call_args[0][0]
  assert JSONRPCEncoder.encode(msg.params) == '{"protocol":"signalwire-proto-test","method":"calling.connect","params":{"node_id":"node-id","call_id":"call-id","devices":[[{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999990","timeout":30}}]]}}'
  relay_call_active.calling.client.execute.mock.assert_called_once()
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"failed","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call_active.calling, payload)
  assert action.completed
  assert action.result.call is None

@pytest.mark.asyncio
async def test_connect_async_with_failure(fail_response, relay_call_active):
  relay_call_active.calling.client.execute = fail_response
  devices = [
    { 'to_number': '+12029999990', 'timeout': 30 }
  ]
  action = await relay_call_active.connect_async(device_list=devices)
  assert action.completed
  assert action.state == 'failed'
  relay_call_active.calling.client.execute.mock.assert_called_once()
