import asyncio
import json
import pytest
from signalwire.tests import AsyncMock

async def _fire(calling, notification):
  calling.notification_handler(notification)

@pytest.mark.asyncio
async def test_wait_for_ringing(relay_call):
  relay_call.calling.client.execute = AsyncMock()
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ringing","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.wait_for_ringing()
  assert result
  assert relay_call.state == 'ringing'
  relay_call.calling.client.execute.mock.assert_not_called()

@pytest.mark.asyncio
async def test_wait_for_answered(relay_call):
  relay_call.calling.client.execute = AsyncMock()
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.wait_for_answered()
  assert result
  assert relay_call.state == 'answered'
  relay_call.calling.client.execute.mock.assert_not_called()

@pytest.mark.asyncio
async def test_wait_for_answered_on_ending_call(relay_call):
  relay_call.state = 'ending'
  result = await relay_call.wait_for_answered()
  assert result

@pytest.mark.asyncio
async def test_wait_for_ending(relay_call):
  relay_call.calling.client.execute = AsyncMock()
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ending","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.wait_for_ending()
  assert result
  assert relay_call.state == 'ending'
  relay_call.calling.client.execute.mock.assert_not_called()

@pytest.mark.asyncio
async def test_wait_for_ended(relay_call):
  relay_call.calling.client.execute = AsyncMock()
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ended","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.wait_for_ended()
  assert result
  assert relay_call.state == 'ended'
  relay_call.calling.client.execute.mock.assert_not_called()
