import pytest
from signalwire.blade.messages.message import Message
from signalwire.relay.calling import Calling, Call
from unittest.mock import Mock

def test_add_call(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance)
  c2 = Call(calling=instance)
  c3 = Call(calling=instance)
  assert len(instance.calls) == 3

def test_remove_call(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance)
  instance.remove_call(c1)
  assert len(instance.calls) == 0

def test_get_call_by_id(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance, **{ 'call_id': '1234' })
  assert instance._get_call_by_id('1234') is c1

def test_get_call_by_tag(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance, **{ 'call_id': '1234' })
  assert instance._get_call_by_tag(c1.tag) is c1

@pytest.mark.asyncio
async def test_on_receive(relay_calling):
  handler = Mock()
  await relay_calling.receive(['home', 'office'], handler)

  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.receive","timestamp":1569514183.0130031,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","context":"office","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"direction":"inbound","call_id":"call-id","node_id":"node-id"},"context":"office","event_channel":"signalwire-proto-test"}}}')
  relay_calling.client.message_handler(message)

  call = handler.call_args[0][0]
  assert isinstance(call, Call)
  assert call.from_number == '+12029999999'
  assert call.to_number == '+12028888888'
  handler.assert_called_once()

@pytest.mark.asyncio
async def test_on_state_created(relay_calling):
  call = Call(calling=relay_calling)
  assert call.id is None
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)

  assert call.state == 'created'
  assert call.id == 'call-id'
  assert call.node_id == 'node-id'

@pytest.mark.asyncio
async def test_on_state_ringing(relay_calling):
  call = Call(calling=relay_calling)
  call.id = 'call-id'
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"ringing","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)
  assert call.state == 'ringing'
