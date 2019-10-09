import asyncio
import json
import pytest
from unittest.mock import Mock, patch
from signalwire.relay.calling.components.play import Play
from signalwire.relay.calling.actions.play_action import PlayAction

PLAY_STOP_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.stop","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_PAUSE_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.pause","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_RESUME_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.resume","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id"}}')
PLAY_VOLUME_PAYLOAD = json.loads('{"protocol":"signalwire-proto-test","method":"calling.play.volume","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","volume":4.1}}')

@pytest.fixture()
def play_action(relay_call):
  component = Play(relay_call, [{'type': 'audio', 'url': 'audio.mp3'}])
  component.control_id = 'control-id' # force-mock control_id
  return PlayAction(component)

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
