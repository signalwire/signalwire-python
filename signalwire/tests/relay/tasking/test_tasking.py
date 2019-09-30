import pytest
from signalwire.blade.messages.message import Message
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_on_receive(relay_tasking):
  handler = Mock()
  await relay_tasking.receive(['home', 'office'], handler)

  message = Message.from_json('{"jsonrpc":"2.0","id":"uuid","method":"blade.broadcast","params":{"broadcaster_nodeid":"uuid","protocol":"signalwire-proto-test","channel":"notifications","event":"queuing.relay.tasks","params":{"project_id":"project-uuid","space_id":"space-uuid","context":"office","message":{"key":"value","data":"random stuff"},"timestamp":1569859833,"event_channel":"signalwire-proto-test"}}}')
  relay_tasking.client.message_handler(message)

  # call = handler.call_args[0][0]
  # assert isinstance(call, Call)
  # assert call.from_number == '+12029999999'
  # assert call.to_number == '+12028888888'
  handler.assert_called_once()
