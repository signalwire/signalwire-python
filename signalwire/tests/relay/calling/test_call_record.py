import asyncio
import json
import pytest
from unittest.mock import Mock, patch
from signalwire.tests import AsyncMock

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_record_events(relay_call):
  mock = Mock()
  relay_call.on('record.stateChange', mock)
  relay_call.on('record.finished', mock)
  payload = json.loads('{"event_type":"calling.call.record","params":{"state":"finished","record":{"audio":{"format":"mp3","direction":"speak","stereo":false}},"url":"record.mp3","control_id":"control-id","size":4096,"duration":4,"call_id":"call-id","node_id":"node-id"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_record_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.record","params":{"state":"recording","record":{"audio":{"format":"mp3","direction":"speak","stereo":true}},"url":"record.mp3","control_id":"control-id","size":4096,"duration":4,"call_id":"call-id","node_id":"node-id"}}')
    asyncio.create_task(_fire(relay_call.calling, payload)) # Test 'recording' event before 'finished'
    payload = json.loads('{"event_type":"calling.call.record","params":{"state":"finished","record":{"audio":{"format":"mp3","direction":"speak","stereo":true}},"url":"record.mp3","control_id":"control-id","size":4096,"duration":4,"call_id":"call-id","node_id":"node-id"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.record(beep=True, direction='both', terminators='#')
    assert result.successful
    assert result.url == 'record.mp3'
    assert result.duration == 4
    assert result.size == 4096
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.record","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","record":{"audio":{"beep":true,"direction":"both","terminators":"#"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.record(beep=True, direction='both', terminators='#')
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"code":"200","message":"Message","url":"record.mp3"}}')
    relay_call.calling.client.execute = AsyncMock(return_value=relay_response)
    # relay_call.calling.client.execute = success_response
    action = await relay_call.record_async(terminators='#')
    assert not action.completed
    assert action.url == 'record.mp3'
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.record","params":{"state":"finished","record":{"audio":{"format":"mp3","direction":"speak","stereo":true}},"url":"record.mp3","control_id":"control-id","size":4096,"duration":4,"call_id":"call-id","node_id":"node-id"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.record","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","record":{"audio":{"terminators":"#"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_async_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.record_async(beep=True, direction='both', terminators='#')
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_with_no_input_event(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.record","params":{"state":"no_input","control_id":"control-id","call_id":"call-id","node_id":"node-id"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.record(beep=True, direction='both', terminators='#')
    assert not result.successful
    assert result.event.payload['state'] == 'no_input'
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_async_with_no_input_event(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.record_async(terminators='#')
    assert not action.completed
    payload = json.loads('{"event_type":"calling.call.record","params":{"state":"no_input","control_id":"control-id","call_id":"call-id","node_id":"node-id"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    assert not action.result.successful
    relay_call.calling.client.execute.mock.assert_called_once()
