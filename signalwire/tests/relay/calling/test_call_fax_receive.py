import asyncio
import json
import pytest
from unittest.mock import Mock, patch

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_fax_events(relay_call):
  mock = Mock()
  on_page = Mock()
  on_finished = Mock()
  relay_call.on('fax.stateChange', mock)
  relay_call.on('fax.page', on_page)
  relay_call.on('fax.finished', on_finished)
  page_event = json.loads('{"event_type":"calling.call.fax","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","fax":{"type":"page","params":{"direction":"send","pages":"1"}}}}')
  relay_call.calling.notification_handler(page_event)
  finished_event = json.loads('{"event_type":"calling.call.fax","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","fax":{"type":"finished","params":{"direction":"send","identity":"+1xxx","remote_identity":"+1yyy","document":"file.pdf","success":true,"result":"1231","result_text":"","pages":"1"}}}}')
  relay_call.calling.notification_handler(finished_event)
  assert mock.call_count == 2
  assert on_page.call_count == 1
  assert on_finished.call_count == 1

@pytest.mark.asyncio
async def test_fax_receive_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.fax","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","fax":{"type":"finished","params":{"direction":"receive","identity":"+1xxx","remote_identity":"+1yyy","document":"file.pdf","success":true,"result":"1231","result_text":"","pages":"1"}}}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.fax_receive()
    assert result.successful
    assert result.direction == 'receive'
    assert result.identity == '+1xxx'
    assert result.remote_identity == '+1yyy'
    assert result.document == 'file.pdf'
    assert result.pages == '1'
    assert result.event.payload['type'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.receive_fax","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_fax_receive_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.fax_receive()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_fax_receive_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.fax_receive_async()
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.fax","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","fax":{"type":"finished","params":{"direction":"receive","identity":"+1xxx","remote_identity":"+1yyy","document":"file.pdf","success":true,"result":"1231","result_text":"","pages":"1"}}}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.receive_fax","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_fax_receive_async_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.fax_receive_async()
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
