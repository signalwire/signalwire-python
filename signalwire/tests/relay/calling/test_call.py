import asyncio
import json
import pytest
from unittest.mock import Mock

def test_init_options(relay_call):
  assert relay_call.id == 'call-id'
  assert relay_call.node_id == 'node-id'
  assert relay_call.call_type == 'phone'
  assert relay_call.from_number == '+12029999999'
  assert relay_call.to_number == '+12028888888'
  assert relay_call.state == 'created'
  assert relay_call.context == 'office'
  assert relay_call.timeout is None

def test_device(relay_call):
  assert relay_call.device == {'type':'phone','params':{'from_number':'+12029999999','to_number':'+12028888888'}}

async def _fire(calling, notification):
  calling.notification_handler(notification)

def test_on_method(relay_call):
  on_answered = Mock()
  relay_call.on('stateChange', on_answered)
  relay_call.on('answered', on_answered)
  on_ended = Mock()
  relay_call.on('ended', on_ended)
  answered_event = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  relay_call.calling.notification_handler(answered_event)
  assert on_answered.call_count == 2
  on_ended.assert_not_called()
  ended_event = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ended","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"end_reason":"noAnswer","call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  relay_call.calling.notification_handler(ended_event)
  on_ended.assert_called_once()

def test_off_method(relay_call):
  on_answered = Mock()
  relay_call.on('stateChange', on_answered)
  relay_call.on('answered', on_answered)

  relay_call.off('stateChange', on_answered)
  relay_call.off('answered')
  answered_event = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  relay_call.calling.notification_handler(answered_event)
  on_answered.assert_not_called()

@pytest.mark.asyncio
async def test_answer_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.answer()

  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.answer","params":{"call_id":"call-id","node_id":"node-id"}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_answer_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.answer()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_hangup(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ended","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"end_reason":"noAnswer","call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.hangup()

  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.end","params":{"call_id":"call-id","node_id":"node-id","reason":"hangup"}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_hangup_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.hangup()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_dial(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"end_reason":"noAnswer","call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.dial()

  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.begin","params":{"tag":"'+relay_call.tag+'","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}}}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_dial_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.dial()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
