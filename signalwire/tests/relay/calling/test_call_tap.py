import asyncio
import json
import pytest
from unittest.mock import Mock, patch
from signalwire.tests import AsyncMock

@pytest.fixture()
def tap_success_response():
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"code":"200","message":"Tapping","call_id":"call-id","control_id":"control-id","source_device":{"type":"rtp","params":{"addr":"10.10.10.10","port":30030,"codec":"PCMU","ptime":20,"rate":8000}}}}')
  return AsyncMock(return_value=response)

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_tap_events(relay_call):
  mock = Mock()
  relay_call.on('tap.stateChange', mock)
  relay_call.on('tap.finished', mock)
  payload = json.loads('{"event_type":"calling.call.tap","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished","tap":{"type":"audio","params":{"direction":"listen"}},"device":{"type":"rtp","params":{"addr":"127.0.0.1","port":1234,"codec":"PCMU","ptime":20}}}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_tap_with_success(tap_success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = tap_success_response
    payload = json.loads('{"event_type":"calling.call.tap","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished","tap":{"type":"audio","params":{"direction":"listen"}},"device":{"type":"rtp","params":{"addr":"127.0.0.1","port":1234,"codec":"PCMU","ptime":20}}}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.tap(audio_direction='listen', target_type='rtp', target_addr='127.0.0.1', target_port='1234')
    assert result.successful
    assert result.source_device == json.loads('{"type":"rtp","params":{"addr":"10.10.10.10","port":30030,"codec":"PCMU","ptime":20,"rate":8000}}')
    assert result.destination_device == json.loads('{"type":"rtp","params":{"addr":"127.0.0.1","port":1234,"codec":"PCMU","ptime":20}}')
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.tap","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","tap":{"type":"audio","params":{"direction":"listen"}},"device":{"type":"rtp","params":{"addr":"127.0.0.1","port":1234}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_tap_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.tap(audio_direction='listen', target_type='rtp', target_addr='127.0.0.1', target_port='1234')
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_tap_async_with_success(tap_success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = tap_success_response
    action = await relay_call.tap_async(audio_direction='listen', target_type='rtp', target_addr='127.0.0.1', target_port='1234')
    assert not action.completed
    assert action.source_device == json.loads('{"type":"rtp","params":{"addr":"10.10.10.10","port":30030,"codec":"PCMU","ptime":20,"rate":8000}}')
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.tap","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished","tap":{"type":"audio","params":{"direction":"listen"}},"device":{"type":"rtp","params":{"addr":"127.0.0.1","port":1234,"codec":"PCMU","ptime":20}}}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.tap","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","tap":{"type":"audio","params":{"direction":"listen"}},"device":{"type":"rtp","params":{"addr":"127.0.0.1","port":1234}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_tap_async_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.tap_async(audio_direction='listen', target_type='rtp', target_addr='127.0.0.1', target_port='1234')
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
