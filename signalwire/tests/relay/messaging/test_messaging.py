import json
import pytest
from signalwire.blade.messages.message import Message as BladeMessage
from signalwire.relay.messaging import Messaging, Message, SendResult
from unittest.mock import Mock
from signalwire.tests import AsyncMock

@pytest.mark.asyncio
async def test_receive(relay_messaging):
  handler = Mock()
  await relay_messaging.receive(['home', 'office'], handler)

  event = BladeMessage.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.messaging","params":{"event_type":"messaging.receive","space_id":"space-uuid","project_id":"project-uuid","context":"office","timestamp":1570191488.717304,"params":{"message_id":"875029c0-92cf-44ef-b6c0-d250123e833b","context":"office","direction":"outbound","tags":["t1","t2"],"from_number":"+12029999999","to_number":"+12028888888","body":"Hey There, Welcome at SignalWire!","media":[],"segments":1,"message_state":"received"},"event_channel":"signalwire-proto-test"}}}')
  relay_messaging.client.message_handler(event)

  message = handler.call_args[0][0]
  assert isinstance(message, Message)
  assert message.id == '875029c0-92cf-44ef-b6c0-d250123e833b'
  assert message.from_number == '+12029999999'
  assert message.to_number == '+12028888888'
  assert message.state == 'received'
  assert message.tags == ['t1', 't2']
  handler.assert_called_once()

@pytest.mark.asyncio
async def test_state_change(relay_messaging):
  handler = Mock()
  await relay_messaging.state_change(['home', 'office'], handler)

  event = BladeMessage.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.messaging","params":{"event_type":"messaging.state","space_id":"space-uuid","project_id":"project-uuid","context":"office","timestamp":1570191488.717304,"params":{"message_id":"875029c0-92cf-44ef-b6c0-d250123e833b","context":"office","direction":"outbound","tags":[],"from_number":"+12029999999","to_number":"+12028888888","body":"Hey There, Welcome at SignalWire!","media":[],"segments":1,"message_state":"queued"},"event_channel":"signalwire-proto-test"}}}')
  relay_messaging.client.message_handler(event)

  message = handler.call_args[0][0]
  assert isinstance(message, Message)
  assert message.id == '875029c0-92cf-44ef-b6c0-d250123e833b'
  assert message.from_number == '+12029999999'
  assert message.to_number == '+12028888888'
  assert message.state == 'queued'
  assert message.tags == []
  handler.assert_called_once()

@pytest.mark.asyncio
async def test_send_success(relay_messaging):
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"message":"Message accepted","code":"200","message_id":"2c0e265d-4597-470e-9d5d-00581e0874a2"}}')
  relay_messaging.client.execute = AsyncMock(return_value=response)
  result = await relay_messaging.send(from_number='+12029999999', to_number='+12028888888', context='office', body='Hey There, Welcome at SignalWire!')

  assert isinstance(result, SendResult)
  assert result.successful
  assert result.message_id == '2c0e265d-4597-470e-9d5d-00581e0874a2'
  msg = relay_messaging.client.execute.mock.call_args[0][0]
  params = msg.params.pop('params')
  assert msg.params.pop('protocol') == 'signalwire-proto-test'
  assert msg.params.pop('method') == 'messaging.send'
  assert params['from_number'] == '+12029999999'
  assert params['body'] == 'Hey There, Welcome at SignalWire!'
  relay_messaging.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_fail(relay_messaging):
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"message":"Some error","code":"400"}}')
  relay_messaging.client.execute = AsyncMock(return_value=response)
  result = await relay_messaging.send(from_number='+12029999999', to_number='+12028888888', context='office', body='Hey There, Welcome at SignalWire!')

  assert isinstance(result, SendResult)
  assert not result.successful
  assert result.message_id == None
  relay_messaging.client.execute.mock.assert_called_once()
