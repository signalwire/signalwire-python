from uuid import uuid4
from signalwire.blade.handler import trigger, register, unregister, unregister_all
from .constants import CallState, DisconnectReason, ConnectState, CallPlayState, MediaType, RecordType
from .components.dial import Dial
from .components.hangup import Hangup
from .components.answer import Answer
from .components.connect import Connect
from .results.dial_result import DialResult
from .results.hangup_result import HangupResult
from .results.answer_result import AnswerResult
from .results.connect_result import ConnectResult
from .actions.connect_action import ConnectAction
from .components.play import Play
from .results.play_result import PlayResult
from .actions.play_action import PlayAction
from .components.record import Record
from .results.record_result import RecordResult
from .actions.record_action import RecordAction
from .components.awaiter import Awaiter

class Call:
  def __init__(self, *, calling, **kwargs):
    self.calling = calling
    self.tag = str(uuid4())
    self.id = kwargs.get('call_id', None)
    self.node_id = kwargs.get('node_id', None)
    self.context = kwargs.get('context', None)
    if 'device' in kwargs:
      self.call_type = kwargs['device'].get('type', None)
      self.from_number = kwargs['device']['params'].get('from_number', None)
      self.to_number = kwargs['device']['params'].get('to_number', None)
      self.timeout = kwargs['device']['params'].get('timeout', None)
    self.prev_state = None
    self.state = kwargs.get('call_state', None)
    self.peer = None
    self.failed = False
    self.busy = False
    self.calling.add_call(self)

  @property
  def device(self):
    device = {
      'type': self.call_type,
      'params': {
        'from_number': self.from_number,
        'to_number': self.to_number
      }
    }
    if self.timeout is not None:
      device['params']['timeout'] = self.timeout
    return device

  @property
  def answered(self):
    return self.state == CallState.ANSWERED

  @property
  def active(self):
    return self.ended == False

  @property
  def ended(self):
    return self.state == CallState.ENDING or self.state == CallState.ENDED

  def on(self, event, callback):
    register(event=self.tag, callback=callback, suffix=event)
    return self

  def off(self, event, callback=None):
    unregister(event=self.tag, callback=callback, suffix=event)
    return self

  async def dial(self):
    component = Dial(self)
    await component.wait_for(CallState.ANSWERED, CallState.ENDING, CallState.ENDED)
    return DialResult(component)

  async def hangup(self, reason: str = 'hangup'):
    component = Hangup(self, reason)
    await component.wait_for(CallState.ENDED)
    return HangupResult(component)

  async def answer(self):
    component = Answer(self)
    await component.wait_for(CallState.ANSWERED, CallState.ENDING, CallState.ENDED)
    return AnswerResult(component)

  async def connect(self, device_list, ringback_list=[]):
    component = Connect(self, device_list, ringback_list)
    await component.wait_for(ConnectState.FAILED, ConnectState.DISCONNECTED, ConnectState.CONNECTED)
    return ConnectResult(component)

  async def connect_async(self, device_list, ringback_list=[]):
    component = Connect(self, device_list, ringback_list)
    await component.execute()
    return ConnectAction(component)

  async def play(self, media_list, volume=0):
    component = Play(self, media_list, volume)
    await component.wait_for(CallPlayState.ERROR, CallPlayState.FINISHED)
    return PlayResult(component)

  async def play_async(self, media_list, volume=0):
    component = Play(self, media_list, volume)
    await component.execute()
    return PlayAction(component)

  def play_audio(self, url, volume=0):
    media_list = [{ 'type': MediaType.AUDIO, 'url': url }]
    return self.play(media_list, volume)

  def play_audio_async(self, url, volume=0):
    media_list = [{ 'type': MediaType.AUDIO, 'url': url }]
    return self.play_async(media_list, volume)

  def play_silence(self, duration):
    media_list = [{ 'type': MediaType.SILENCE, 'duration': float(duration) }]
    return self.play(media_list)

  def play_silence_async(self, duration):
    media_list = [{ 'type': MediaType.SILENCE, 'duration': float(duration) }]
    return self.play_async(media_list)

  def play_tts(self, text, language=None, gender=None, volume=0):
    media = { 'type': MediaType.TTS, 'text': text }
    if language:
      media['language'] = language
    if gender:
      media['gender'] = gender
    return self.play([ media ], volume)

  def play_tts_async(self, text, language=None, gender=None, volume=0):
    media = { 'type': MediaType.TTS, 'text': text }
    if language:
      media['language'] = language
    if gender:
      media['gender'] = gender
    return self.play_async([ media ], volume)

  async def record(self, record_type=RecordType.AUDIO, beep=None, record_format=None, stereo=None, direction=None, initial_timeout=None, end_silence_timeout=None, terminators=None):
    component = Record(self, record_type, beep, record_format, stereo, direction, initial_timeout, end_silence_timeout, terminators)
    await component.wait_for(CallPlayState.ERROR, CallPlayState.FINISHED)
    return RecordResult(component)

  async def record_async(self, record_type=RecordType.AUDIO, beep=None, record_format=None, stereo=None, direction=None, initial_timeout=None, end_silence_timeout=None, terminators=None):
    component = Record(self, record_type, beep, record_format, stereo, direction, initial_timeout, end_silence_timeout, terminators)
    result = await component.execute()
    if result and 'url' in result:
      component.url = result['url']
    return RecordAction(component)

  async def wait_for(self, events=[CallState.ENDED]):
    state_index = CallState.ALL.index(self.state)
    for event in events:
      if CallState.ALL.index(event) <= state_index:
        return True
    component = Awaiter(self)
    await component.wait_for(*events)
    return component.successful

  def wait_for_ringing(self):
    return self.wait_for(events=[CallState.RINGING])

  def wait_for_answered(self):
    return self.wait_for(events=[CallState.ANSWERED])

  def wait_for_ending(self):
    return self.wait_for(events=[CallState.ENDING])

  def wait_for_ended(self):
    return self.wait_for(events=[CallState.ENDED])

  def _state_changed(self, params):
    self.prev_state = self.state
    self.state = params['call_state']
    trigger(self.tag, params, suffix='stateChange')
    trigger(self.tag, params, suffix=self.state)
    if self.state == CallState.ENDED:
      check_id = self.id if self.id else self.tag
      trigger(check_id, params, suffix=CallState.ENDED) # terminate components
      unregister_all(self.tag) # unregister all external handlers
      end_reason = params.get('end_reason', '')
      self.failed = end_reason == DisconnectReason.ERROR
      self.busy = end_reason == DisconnectReason.BUSY
      self.calling.remove_call(self)
