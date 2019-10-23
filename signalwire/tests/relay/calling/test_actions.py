import asyncio
import json
import pytest
from unittest.mock import Mock, patch
from signalwire.relay.calling.components.play import Play
from signalwire.relay.calling.actions.play_action import PlayAction
from signalwire.relay.calling.components.record import Record
from signalwire.relay.calling.actions.record_action import RecordAction
from signalwire.relay.calling.components.fax_send import FaxSend
from signalwire.relay.calling.components.fax_receive import FaxReceive
from signalwire.relay.calling.actions.fax_action import FaxAction
from signalwire.relay.calling.components.tap import Tap
from signalwire.relay.calling.actions.tap_action import TapAction
from signalwire.relay.calling.components.detect import Detect
from signalwire.relay.calling.actions.detect_action import DetectAction
from signalwire.relay.calling.components.prompt import Prompt
from signalwire.relay.calling.actions.prompt_action import PromptAction

PLAY_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_PAUSE_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.pause","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_RESUME_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.resume","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_VOLUME_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.volume","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","volume":4.1}}')
RECORD_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.record.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
RECEIVE_FAX_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.receive_fax.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
SEND_FAX_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.send_fax.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
TAP_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.tap.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
DETECT_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.detect.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PROMPT_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PROMPT_VOLUME_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect.volume","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","volume":-5.4}}')

@pytest.fixture()
def play_action(relay_call):
  component = Play(relay_call, [{'type': 'audio', 'url': 'audio.mp3'}])
  component.control_id = 'control-id' # force-mock control_id
  return PlayAction(component)

@pytest.fixture()
def record_action(relay_call):
  component = Record(relay_call, beep=True, terminators='#')
  component.control_id = 'control-id' # force-mock control_id
  return RecordAction(component)

@pytest.fixture()
def send_fax_action(relay_call):
  component = FaxSend(relay_call, document='file.pdf')
  component.control_id = 'control-id' # force-mock control_id
  return FaxAction(component)

@pytest.fixture()
def receive_fax_action(relay_call):
  component = FaxReceive(relay_call)
  component.control_id = 'control-id' # force-mock control_id
  return FaxAction(component)

@pytest.fixture()
def tap_action(relay_call):
  component = Tap(relay_call, audio_direction='both', target_type='rtp')
  component.control_id = 'control-id' # force-mock control_id
  return TapAction(component)

@pytest.fixture()
def detect_action(relay_call):
  component = Detect(relay_call, 'machine')
  component.control_id = 'control-id' # force-mock control_id
  return DetectAction(component)

@pytest.fixture()
def prompt_action(relay_call):
  component = Prompt(relay_call, 'both', [])
  component.control_id = 'control-id' # force-mock control_id
  return PromptAction(component)

@pytest.mark.asyncio
async def test_play_action_stop_with_success(success_response, relay_call, play_action):
  relay_call.calling.client.execute = success_response
  result = await play_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_stop_with_failure(fail_response, relay_call, play_action):
  relay_call.calling.client.execute = fail_response
  result = await play_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_pause_with_success(success_response, relay_call, play_action):
  relay_call.calling.client.execute = success_response
  result = await play_action.pause()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_PAUSE_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_pause_with_failure(fail_response, relay_call, play_action):
  relay_call.calling.client.execute = fail_response
  result = await play_action.pause()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_PAUSE_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_resume_with_success(success_response, relay_call, play_action):
  relay_call.calling.client.execute = success_response
  result = await play_action.resume()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_RESUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_resume_with_failure(fail_response, relay_call, play_action):
  relay_call.calling.client.execute = fail_response
  result = await play_action.resume()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_RESUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_volume_with_success(success_response, relay_call, play_action):
  relay_call.calling.client.execute = success_response
  result = await play_action.volume(4.1)
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_VOLUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_action_volume_with_failure(fail_response, relay_call, play_action):
  relay_call.calling.client.execute = fail_response
  result = await play_action.volume(4.1)
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PLAY_VOLUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_action_stop_with_success(success_response, relay_call, record_action):
  relay_call.calling.client.execute = success_response
  result = await record_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == RECORD_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_record_action_stop_with_failure(fail_response, relay_call, record_action):
  relay_call.calling.client.execute = fail_response
  result = await record_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == RECORD_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_fax_action_stop_with_success(success_response, relay_call, send_fax_action):
  relay_call.calling.client.execute = success_response
  result = await send_fax_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == SEND_FAX_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_send_fax_action_stop_with_failure(fail_response, relay_call, send_fax_action):
  relay_call.calling.client.execute = fail_response
  result = await send_fax_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == SEND_FAX_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_receive_fax_action_stop_with_success(success_response, relay_call, receive_fax_action):
  relay_call.calling.client.execute = success_response
  result = await receive_fax_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == RECEIVE_FAX_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_receive_fax_action_stop_with_failure(fail_response, relay_call, receive_fax_action):
  relay_call.calling.client.execute = fail_response
  result = await receive_fax_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == RECEIVE_FAX_STOP_PAYLOAD

@pytest.mark.asyncio
async def test_tap_action_stop_with_success(success_response, relay_call, tap_action):
  relay_call.calling.client.execute = success_response
  result = await tap_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == TAP_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_tap_action_stop_with_failure(fail_response, relay_call, tap_action):
  relay_call.calling.client.execute = fail_response
  result = await tap_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == TAP_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_action_stop_with_success(success_response, relay_call, detect_action):
  relay_call.calling.client.execute = success_response
  result = await detect_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == DETECT_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_detect_action_stop_with_failure(fail_response, relay_call, detect_action):
  relay_call.calling.client.execute = fail_response
  result = await detect_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == DETECT_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_action_stop_with_success(success_response, relay_call, prompt_action):
  relay_call.calling.client.execute = success_response
  result = await prompt_action.stop()
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PROMPT_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_action_stop_with_failure(fail_response, relay_call, prompt_action):
  relay_call.calling.client.execute = fail_response
  result = await prompt_action.stop()
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PROMPT_STOP_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_action_volume_with_success(success_response, relay_call, prompt_action):
  relay_call.calling.client.execute = success_response
  result = await prompt_action.volume(-5.4)
  assert result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PROMPT_VOLUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_action_volume_with_failure(fail_response, relay_call, prompt_action):
  relay_call.calling.client.execute = fail_response
  result = await prompt_action.volume(-5.4)
  assert not result.successful
  msg = relay_call.calling.client.execute.mock.call_args[0][0]
  assert msg.params == PROMPT_VOLUME_PAYLOAD
  relay_call.calling.client.execute.mock.assert_called_once()
