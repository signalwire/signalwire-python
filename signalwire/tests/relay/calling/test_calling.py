import pytest
from signalwire.blade.messages.message import Message
from signalwire.relay.calling import Calling, Call
from signalwire.relay.calling.devices import PhoneDevice, AgoraDevice, SipDevice
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
async def test_on_receive_phone_call(relay_calling):
  handler = Mock()
  await relay_calling.receive(['home', 'office'], handler)

  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.receive","timestamp":1569514183.0130031,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","context":"office","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"direction":"inbound","call_id":"call-id","node_id":"node-id"},"context":"office","event_channel":"signalwire-proto-test"}}}')
  relay_calling.client.message_handler(message)

  call = handler.call_args[0][0]
  assert isinstance(call, Call)
  assert isinstance(call.device, PhoneDevice)
  assert call.call_type == 'phone'
  assert call.from_endpoint == '+12029999999'
  assert call.to_endpoint == '+12028888888'
  handler.assert_called_once()

@pytest.mark.asyncio
async def test_on_receive_agora_call(relay_calling):
  handler = Mock()
  await relay_calling.receive(['home', 'office'], handler)

  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.receive","timestamp":1569514183.0130031,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","context":"office","device":{"type":"agora","params":{"to":"+15551231234","from":"+15551231245","appid":"uuid","channel":"1111","timeout":60}},"direction":"inbound","call_id":"call-id","node_id":"node-id"},"context":"office","event_channel":"signalwire-proto-test"}}}')
  relay_calling.client.message_handler(message)

  call = handler.call_args[0][0]
  assert isinstance(call, Call)
  assert isinstance(call.device, AgoraDevice)
  assert call.call_type == 'agora'
  assert call.from_endpoint == '+15551231245'
  assert call.to_endpoint == '+15551231234'
  assert call.timeout == 60
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

def test_new_call_with_flattened_params_old_way(relay_calling):
  call = relay_calling.new_call(call_type='phone', from_number='+12029999999', to_number='+12028888888', timeout=50)
  assert isinstance(call, Call)
  assert len(call.targets) == 1
  # dispatch relay events
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)
  assert len(call.attempted_devices) == 1
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888","timeout":50}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)

  assert isinstance(call.device, PhoneDevice)
  assert call.call_type == 'phone'
  assert call.from_endpoint == '+12029999999'
  assert call.to_endpoint == '+12028888888'
  assert call.timeout == 50

def test_new_call_with_flattened_params_old_way_sip(relay_calling):
  call = relay_calling.new_call(call_type='sip', from_number='user@domain.sip.com', to_number='user@other.sip.com')
  assert isinstance(call, Call)
  assert len(call.targets) == 1
  # dispatch relay events
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"created","direction":"outbound","device":{"type":"sip","params":{"from":"user@domain.sip.com","to":"user@other.sip.com"}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)
  assert isinstance(call.attempted_devices[0], SipDevice)
  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.events","params":{"event_type":"calling.call.state","event_channel":"signalwire-proto-test","timestamp":1569517309.4546909,"project_id":"project-uuid","space_id":"space-uuid","params":{"call_state":"answered","direction":"outbound","device":{"type":"sip","params":{"from":"user@domain.sip.com","to":"user@other.sip.com"}},"call_id":"call-id","node_id":"node-id","tag":"'+call.tag+'"}}}}')
  relay_calling.client.message_handler(message)

  assert isinstance(call.device, SipDevice)
  assert call.call_type == 'sip'
  assert call.from_endpoint == 'user@domain.sip.com'
  assert call.to_endpoint == 'user@other.sip.com'
