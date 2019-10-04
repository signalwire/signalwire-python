import asyncio
import json
import pytest
from signalwire.relay.calling import Call

@pytest.fixture()
def relay_call(relay_calling):
  params = json.loads('{"call_state":"created","context":"office","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"direction":"inbound","call_id":"call-id","node_id":"node-id"}')
  return Call(calling=relay_calling, **params)

async def _fire(calling, notification):
  calling.notification_handler(notification)

@pytest.mark.asyncio
async def test_connect_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  payload = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1570204684.1133151,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.connect()

  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.answer","params":{"call_id":"call-id","node_id":"node-id"}}')
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_connect_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.connect()
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()
