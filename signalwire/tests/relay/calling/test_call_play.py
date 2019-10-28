import asyncio
import json
import pytest
from unittest.mock import Mock, patch

async def _fire(calling, notification):
  calling.notification_handler(notification)

def mock_uuid():
  return 'control-id'

def test_play_events(relay_call):
  mock = Mock()
  relay_call.on('play.stateChange', mock)
  relay_call.on('play.finished', mock)
  payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2

@pytest.mark.asyncio
async def test_play_multiple_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"playing"}}')
    asyncio.create_task(_fire(relay_call.calling, payload)) # Test 'playing' event before 'finished'
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    media = [
      { 'type': 'audio', 'url': 'audio.mp3' },
      { 'type': 'tts', 'text': 'welcome', 'gender': 'male' },
      { 'type': 'silence', 'duration': 5 }
    ]
    result = await relay_call.play(media_list=media)
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}},{"type":"tts","params":{"text":"welcome","gender":"male"}},{"type":"silence","params":{"duration":5}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_multiple_media_volume_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    media = [
      { 'type': 'audio', 'url': 'audio.mp3' },
      { 'type': 'tts', 'text': 'welcome', 'gender': 'male' },
      { 'type': 'silence', 'duration': 5 }
    ]
    result = await relay_call.play(media_list=media, volume=-3.2)
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}},{"type":"tts","params":{"text":"welcome","gender":"male"}},{"type":"silence","params":{"duration":5}}],"volume":-3.2}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_multiple_media_with_failure(fail_response, relay_call):
  relay_call.calling.client.execute = fail_response
  media = [
    { 'type': 'audio', 'url': 'audio.mp3' },
    { 'type': 'tts', 'text': 'welcome', 'gender': 'male' },
    { 'type': 'silence', 'duration': 5 }
  ]
  result = await relay_call.play(media_list=media)
  assert not result.successful
  relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_async_multiple_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    media = [
      { 'type': 'audio', 'url': 'audio.mp3' },
      { 'type': 'tts', 'text': 'welcome', 'gender': 'male' },
      { 'type': 'silence', 'duration': 5 }
    ]
    action = await relay_call.play_async(media_list=media, volume=4.3)
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}},{"type":"tts","params":{"text":"welcome","gender":"male"}},{"type":"silence","params":{"duration":5}}],"volume":4.3}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_audio_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.play_audio('audio.mp3')
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_audio_async_multiple_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.play_audio_async('audio.mp3')
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"audio","params":{"url":"audio.mp3"}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_tts_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.play_tts(text='welcome', gender='male')
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"tts","params":{"text":"welcome","gender":"male"}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_tts_async_multiple_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.play_tts_async(text='welcome', gender='male', volume=5.0)
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"tts","params":{"text":"welcome","gender":"male"}}],"volume":5.0}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_silence_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.play_silence('5')
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"silence","params":{"duration":5}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_silence_async_multiple_media_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.play_silence_async('5')
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"silence","params":{"duration":5}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_multiple_media_with_error_event(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"error"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    media = [
      { 'type': 'audio', 'url': 'audio.mp3' }
    ]
    result = await relay_call.play(media_list=media)
    assert not result.successful
    assert result.event.payload['state'] == 'error'
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_async_multiple_media_with_error_event(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    media = [
      { 'type': 'audio', 'url': 'audio.mp3' }
    ]
    action = await relay_call.play_async(media_list=media)
    assert not action.completed
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"error"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    assert not action.result.successful
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_ringtone_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    asyncio.create_task(_fire(relay_call.calling, payload))
    result = await relay_call.play_ringtone(name='us')
    assert result.successful
    assert result.event.payload['state'] == 'finished'
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"ringtone","params":{"name":"us"}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()

@pytest.mark.asyncio
async def test_play_ringtone_async_with_success(success_response, relay_call):
  with patch('signalwire.relay.calling.components.uuid4', mock_uuid):
    relay_call.calling.client.execute = success_response
    action = await relay_call.play_ringtone_async(duration=40, name='us')
    assert not action.completed
    # Complete the action now..
    payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
    await _fire(relay_call.calling, payload)
    assert action.completed
    msg = relay_call.calling.client.execute.mock.call_args[0][0]
    assert msg.params == json.loads('{"protocol":"signalwire-proto-test","method":"calling.play","params":{"call_id":"call-id","node_id":"node-id","control_id":"control-id","play":[{"type":"ringtone","params":{"name":"us","duration":40}}]}}')
    relay_call.calling.client.execute.mock.assert_called_once()
