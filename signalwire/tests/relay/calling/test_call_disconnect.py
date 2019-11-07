import asyncio
import json
import pytest
from unittest.mock import Mock
from signalwire.relay.calling.call import Call

async def _fire(calling, notification):
  calling.notification_handler(notification)

def test_disconnect_events(relay_call):
  mock = Mock()
  relay_call.on('connect.stateChange', mock)
  relay_call.on('connect.disconnected', mock)
  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"disconnected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_disconnect_with_success(success_response, relay_call):
  relay_call.calling.client.execute = success_response
  peer_created = json.loads('{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","direction":"outbound","peer":{"call_id":"call-id","node_id":"node-id"},"device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"peer-call-id","node_id":"peer-node-id"}}')
  await _fire(relay_call.calling, peer_created)

  payload = json.loads('{"event_type":"calling.call.connect","params":{"connect_state":"connected","peer":{"call_id":"peer-call-id","node_id":"peer-node-id","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12029999991"}}},"call_id":"call-id","node_id":"node-id","tag":"call-tag"}}')
  await _fire(relay_call.calling, payload)
  assert isinstance(relay_call.peer, Call)

  payload['params']['connect_state'] = 'disconnected'
  asyncio.create_task(_fire(relay_call.calling, payload))
  result = await relay_call.disconnect()
  assert result.successful
  assert relay_call.peer is None
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.disconnect","params":{"call_id":"call-id","node_id":"node-id"}}')
  relay_call.calling.client.execute.mock.assert_called_once()
