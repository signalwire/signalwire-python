import asyncio
import json
import pytest
from unittest.mock import Mock, patch

DIGIT = json.loads('{"event_type":"calling.call.collect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","result":{"type":"digit","params":{"digits":"12345","terminator":"#"}}}}')
SPEECH = json.loads('{"event_type":"calling.call.collect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","result":{"type":"speech","params":{"text":"example hello","confidence":83.4}}}}')
ERROR = json.loads('{"event_type":"calling.call.collect","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","result":{"type":"error"}}}')

@pytest.fixture()
def media_list():
  return [{ 'type': 'audio', 'url': 'audio.mp3' }]

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_prompt_events(relay_call):
  mock = Mock()
  relay_call.on('prompt', mock)
  relay_call.calling.notification_handler(DIGIT)
  assert mock.call_count == 1

@pytest.mark.asyncio
async def test_prompt_both_with_success(success_response, relay_call, media_list):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, DIGIT))
    result = await relay_call.prompt(prompt_type='both', media_list=media_list)
    assert result.successful
    assert result.prompt_type == 'digit'
    assert result.result == '12345'
    assert result.terminator == '#'
    assert result.confidence is None
    assert result.event.payload['params']['digits'] == '12345'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"digits":{},"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_speech_with_success(success_response, relay_call, media_list):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, SPEECH))
    result = await relay_call.prompt(prompt_type='speech', media_list=media_list)
    assert result.successful
    assert result.prompt_type == 'speech'
    assert result.result == 'example hello'
    assert result.terminator is None
    assert result.confidence == 83.4
    assert result.event.payload['params']['text'] == 'example hello'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_digits_with_success(success_response, relay_call, media_list):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, DIGIT))
    result = await relay_call.prompt(prompt_type='digits', media_list=media_list, digits_max=5, digits_timeout=30)
    assert result.successful
    assert result.prompt_type == 'digit'
    assert result.result == '12345'
    assert result.terminator == '#'
    assert result.confidence is None
    assert result.event.payload['params']['digits'] == '12345'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"digits":{"max":5,"digit_timeout":30}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_with_error_event(success_response, relay_call, media_list):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, ERROR))
    result = await relay_call.prompt(prompt_type='both', media_list=media_list)
    assert not result.successful
    assert result.prompt_type == 'error'
    assert result.result is None
    assert result.terminator is None
    assert result.confidence is None
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_with_failure(fail_response, relay_call, media_list):
  relay_call.calling.client.execute = fail_response
  result = await relay_call.prompt(prompt_type='both', media_list=media_list)
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_async_with_success(success_response, relay_call, media_list):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.prompt_async(prompt_type='both', media_list=media_list)
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, DIGIT)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"digits":{},"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_async_with_failure(fail_response, relay_call, media_list):
  relay_call.calling.client.execute = fail_response
  action = await relay_call.prompt_async(prompt_type='both', media_list=media_list)
  assert action.completed
  assert not action.result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_audio(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, DIGIT))
    result = await relay_call.prompt_audio(prompt_type='both', url='audio.mp3', digits_max=5)
    assert result.successful
    assert result.prompt_type == 'digit'
    assert result.result == '12345'
    assert result.terminator == '#'
    assert result.confidence is None
    assert result.event.payload['params']['digits'] == '12345'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"digits":{"max":5},"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_audio_async(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.prompt_audio_async(prompt_type='both', url='audio.mp3', speech_language="it-IT")
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, DIGIT)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}],"collect":{"digits":{},"speech":{"language":"it-IT"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_tts(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, SPEECH))
    result = await relay_call.prompt_tts(prompt_type='both', text='hi there!', gender='male', digits_max=5)
    assert result.successful
    assert result.prompt_type == 'speech'
    assert result.result == 'example hello'
    assert result.terminator is None
    assert result.confidence == 83.4
    assert result.event.payload['params']['text'] == 'example hello'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"tts","params":{"text":"hi there!","gender":"male"}}],"collect":{"digits":{"max":5},"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_tts_async(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.prompt_tts_async(prompt_type='both', text='hi there!', gender='male', speech_language="it-IT")
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, SPEECH)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"tts","params":{"text":"hi there!","gender":"male"}}],"collect":{"digits":{},"speech":{"language":"it-IT"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_ringtone(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    asyncio.create_task(_fire(relay_call.calling, SPEECH))
    result = await relay_call.prompt_ringtone(prompt_type='both', name='us', duration=10, digits_max=5)
    assert result.successful
    assert result.prompt_type == 'speech'
    assert result.result == 'example hello'
    assert result.terminator is None
    assert result.confidence == 83.4
    assert result.event.payload['params']['text'] == 'example hello'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"ringtone","params":{"name":"us","duration":10}}],"collect":{"digits":{"max":5},"speech":{}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_ringtone_async(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.prompt_ringtone_async(prompt_type='both', name='us', speech_language="it-IT")
    assert not action.completed
    # Complete the action now..
    await _fire(relay_call.calling, SPEECH)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play_and_collect","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"ringtone","params":{"name":"us"}}],"collect":{"digits":{},"speech":{"language":"it-IT"}}}}')
    relay_call.calling.client.execute.mock.assert_called_once()
