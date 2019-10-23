import asyncio
import json
import pytest
from unittest.mock import Mock, patch

FAX_CED = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"fax","params":{"event":"CED"}}}}')
FAX_ERROR = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"fax","params":{"event":"error"}}}}')
FAX_FINISHED = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"fax","params":{"event":"finished"}}}}')
MACHINE_MACHINE = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"MACHINE"}}}}')
MACHINE_UNKNOWN = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"UNKNOWN"}}}}')
MACHINE_HUMAN = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"HUMAN"}}}}')
MACHINE_READY = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"READY"}}}}')
MACHINE_NOT_READY = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"NOT_READY"}}}}')
MACHINE_ERROR = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"error"}}}}')
MACHINE_FINISHED = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"machine","params":{"event":"finished"}}}}')
DIGIT_DTMF = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"digit","params":{"event":"12"}}}}')
DIGIT_ERROR = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"digit","params":{"event":"error"}}}}')
DIGIT_FINISHED = json.loads('{"event_type":"calling.call.detect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","detect":{"type":"digit","params":{"event":"finished"}}}}')

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_detect_events(relay_call):
  on_update = Mock()
  relay_call.on('detect.update', on_update)
  on_finished = Mock()
  relay_call.on('detect.finished', on_finished)
  relay_call.calling.notification_handler(FAX_CED)
  relay_call.calling.notification_handler(FAX_FINISHED)
  assert on_update.call_count == 1
  assert on_finished.call_count == 1

def test_amd_aliases(relay_call):
  assert relay_call.amd == relay_call.detect_answering_machine
  assert relay_call.amd_async == relay_call.detect_answering_machine_async

@pytest.mark.asyncio
async def test_detect_with_machine_result_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, MACHINE_MACHINE)) # 'MACHINE' will unblock the sync method
    asyncio.create_task(_fire(relay_call.calling, MACHINE_FINISHED)) # This will be ignored
    result = await relay_call.detect('machine', timeout=30)
    assert result.successful
    assert result.detect_type == 'machine'
    assert result.result == 'MACHINE'
    assert result.event.payload['params']['event'] == 'MACHINE'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{}},"timeout":30}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_with_human_result_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, MACHINE_HUMAN)) # 'HUMAN' will unblock the sync method
    asyncio.create_task(_fire(relay_call.calling, MACHINE_FINISHED)) # This will be ignored
    result = await relay_call.detect('machine', timeout=30)
    assert result.successful
    assert result.detect_type == 'machine'
    assert result.result == 'HUMAN'
    assert result.event.payload['params']['event'] == 'HUMAN'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{}},"timeout":30}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_reaching_finished_without_timeout(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, MACHINE_FINISHED))
    result = await relay_call.detect('machine')
    assert not result.successful
    assert result.detect_type == 'machine'
    assert result.result == 'finished'
    assert result.event.payload['params']['event'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_waiting_for_beep(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, MACHINE_MACHINE)) # Fire that's a MACHINE
    asyncio.create_task(_fire(relay_call.calling, MACHINE_NOT_READY)) # NOT_READY will be ignored
    asyncio.create_task(_fire(relay_call.calling, MACHINE_READY)) # READY unblock
    asyncio.create_task(_fire(relay_call.calling, MACHINE_FINISHED)) # FINISHED will be ignored
    result = await relay_call.detect('machine', initial_timeout=5, wait_for_beep=True)
    assert result.successful
    assert result.detect_type == 'machine'
    assert result.result == 'MACHINE'
    assert result.event.payload['params']['event'] == 'READY'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{"initial_timeout":5}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.detect('machine', timeout=30)
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.detect_async('digit', digits='1234')
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, DIGIT_DTMF) # get digits one time '12'
    await _fire(relay_call.calling, DIGIT_DTMF) # get digits second time '12'
    await _fire(relay_call.calling, DIGIT_FINISHED)
    assert action.completed
    assert action.result.result == '12,12'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"digit","params":{"digits":"1234"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_async_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.detect_async('digit', digits='1234')
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_amd_waiting_for_beep(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, MACHINE_MACHINE)) # Fire that's a MACHINE
    asyncio.create_task(_fire(relay_call.calling, MACHINE_NOT_READY)) # NOT_READY will be ignored
    asyncio.create_task(_fire(relay_call.calling, MACHINE_READY)) # READY unblock
    asyncio.create_task(_fire(relay_call.calling, MACHINE_FINISHED)) # FINISHED will be ignored
    result = await relay_call.detect_answering_machine(wait_for_beep=True, end_silence_timeout=5)
    assert result.successful
    assert result.detect_type == 'machine'
    assert result.result == 'MACHINE'
    assert result.event.payload['params']['event'] == 'READY'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{"end_silence_timeout":5}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_amd_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.detect_answering_machine_async(end_silence_timeout=5)
    await _fire(relay_call.calling, MACHINE_MACHINE)
    await _fire(relay_call.calling, MACHINE_NOT_READY)
    await _fire(relay_call.calling, MACHINE_READY)
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, MACHINE_FINISHED)
    assert action.completed
    assert action.result.result == 'MACHINE,NOT_READY,READY'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"machine","params":{"end_silence_timeout":5}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_fax_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, FAX_CED))
    asyncio.create_task(_fire(relay_call.calling, FAX_FINISHED))
    result = await relay_call.detect_fax()
    assert result.successful
    assert result.detect_type == 'fax'
    assert result.result == 'CED'
    assert result.event.payload['params']['event'] == 'CED'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"fax","params":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_fax_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.detect_fax_async(tone='CED')
    await _fire(relay_call.calling, FAX_CED)
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, FAX_FINISHED)
    assert action.completed
    assert action.result.result == 'CED'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"fax","params":{"tone":"CED"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_digit_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, DIGIT_DTMF))
    asyncio.create_task(_fire(relay_call.calling, DIGIT_FINISHED))
    result = await relay_call.detect_digit()
    assert result.successful
    assert result.detect_type == 'digit'
    assert result.result == '12'
    assert result.event.payload['params']['event'] == '12'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"digit","params":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_digit_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.detect_digit_async(digits='#*123')
    await _fire(relay_call.calling, DIGIT_DTMF)
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, DIGIT_FINISHED)
    assert action.completed
    assert action.result.result == '12'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","detect":{"type":"digit","params":{"digits":"#*123"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()
