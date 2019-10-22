import asyncio
import json
import pytest
from unittest.mock import Mock, patch

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_send_digits_events(relay_call):
  mock = Mock()
  relay_call.on('sendDigits.stateChange', mock)
  relay_call.on('sendDigits.finished', mock)
  payload = json.loads('{"event_type":"calling.call.send_digits","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_send_digits_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.send_digits","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.send_digits(digits='1234')
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.send_digits","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","digits":"1234"}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_digits_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.send_digits(digits='1234')
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_digits_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.send_digits_async(digits='1234')
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.send_digits","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.send_digits","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","digits":"1234"}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_digits_async_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.send_digits_async(digits='1234')
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
