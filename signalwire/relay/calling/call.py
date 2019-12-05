from uuid import uuid4
from signalwire.blade.handler import trigger, register, unregister, unregister_all
from .constants import CallState, DisconnectReason, ConnectState, CallPlayState, MediaType, RecordType, TapType, CallTapState, CallFaxState, CallSendDigitsState, DetectState, DetectType, PromptState
from .helpers import prepare_prompt_media_list
from .components.dial import Dial
from .components.hangup import Hangup
from .components.answer import Answer
from .components.connect import Connect
from .results.dial_result import DialResult
from .results.hangup_result import HangupResult
from .results.answer_result import AnswerResult
from .results.connect_result import ConnectResult
from .actions.connect_action import ConnectAction
from .components.detect import Detect
from .results.detect_result import DetectResult
from .actions.detect_action import DetectAction
from .components.play import Play
from .results.play_result import PlayResult
from .actions.play_action import PlayAction
from .components.prompt import Prompt
from .results.prompt_result import PromptResult
from .actions.prompt_action import PromptAction
from .components.record import Record
from .results.record_result import RecordResult
from .actions.record_action import RecordAction
from .components.awaiter import Awaiter
from .components.fax_send import FaxSend
from .components.fax_receive import FaxReceive
from .results.fax_result import FaxResult
from .actions.fax_action import FaxAction
from .components.send_digits import SendDigits
from .results.send_digits_result import SendDigitsResult
from .actions.send_digits_action import SendDigitsAction
from .components.tap import Tap
from .results.tap_result import TapResult
from .actions.tap_action import TapAction
from .components.disconnect import Disconnect
from .results.disconnect_result import DisconnectResult

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

  async def disconnect(self):
    component = Disconnect(self)
    await component.wait_for(ConnectState.FAILED, ConnectState.DISCONNECTED)
    return DisconnectResult(component)

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

  async def detect(self, detect_type, wait_for_beep=False, timeout=None, initial_timeout=None, end_silence_timeout=None, machine_voice_threshold=None, machine_words_threshold=None, tone=None, digits=None):
    component = Detect(self, detect_type, wait_for_beep, timeout, initial_timeout, end_silence_timeout, machine_voice_threshold, machine_words_threshold, tone, digits)
    await component.wait_for(DetectState.MACHINE, DetectState.HUMAN, DetectState.UNKNOWN, DetectState.CED, DetectState.CNG)
    return DetectResult(component)

  async def detect_async(self, detect_type, wait_for_beep=False, timeout=None, initial_timeout=None, end_silence_timeout=None, machine_voice_threshold=None, machine_words_threshold=None, tone=None, digits=None):
    component = Detect(self, detect_type, wait_for_beep, timeout, initial_timeout, end_silence_timeout, machine_voice_threshold, machine_words_threshold, tone, digits)
    await component.execute()
    return DetectAction(component)

  def detect_answering_machine(self, wait_for_beep=False, timeout=None, initial_timeout=None, end_silence_timeout=None, machine_voice_threshold=None, machine_words_threshold=None):
    return self.detect(DetectType.MACHINE, wait_for_beep=wait_for_beep, timeout=timeout, initial_timeout=initial_timeout, end_silence_timeout=end_silence_timeout, machine_voice_threshold=machine_voice_threshold, machine_words_threshold=machine_words_threshold)

  amd = detect_answering_machine

  def detect_answering_machine_async(self, wait_for_beep=False, timeout=None, initial_timeout=None, end_silence_timeout=None, machine_voice_threshold=None, machine_words_threshold=None):
    return self.detect_async(DetectType.MACHINE, wait_for_beep=wait_for_beep, timeout=timeout, initial_timeout=initial_timeout, end_silence_timeout=end_silence_timeout, machine_voice_threshold=machine_voice_threshold, machine_words_threshold=machine_words_threshold)

  amd_async = detect_answering_machine_async

  def detect_fax(self, tone=None, timeout=None):
    return self.detect(DetectType.FAX, tone=tone, timeout=timeout)

  def detect_fax_async(self, tone=None, timeout=None):
    return self.detect_async(DetectType.FAX, tone=tone, timeout=timeout)

  def detect_digit(self, digits=None, timeout=None):
    return self.detect(DetectType.DIGIT, digits=digits, timeout=timeout)

  def detect_digit_async(self, digits=None, timeout=None):
    return self.detect_async(DetectType.DIGIT, digits=digits, timeout=timeout)

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

  def play_ringtone(self, name, duration=None, volume=0):
    media = { 'type': MediaType.RINGTONE, 'name': name }
    if duration:
      media['duration'] = float(duration)
    return self.play([ media ], volume)

  def play_ringtone_async(self, name, duration=None, volume=0):
    media = { 'type': MediaType.RINGTONE, 'name': name }
    if duration:
      media['duration'] = float(duration)
    return self.play_async([ media ], volume)

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

  async def prompt(self, prompt_type, media_list, **kwargs):
    component = Prompt(self, prompt_type, media_list, **kwargs)
    await component.wait_for(PromptState.ERROR, PromptState.NO_INPUT, PromptState.NO_MATCH, PromptState.DIGIT, PromptState.SPEECH)
    return PromptResult(component)

  async def prompt_async(self, prompt_type, media_list, **kwargs):
    component = Prompt(self, prompt_type, media_list, **kwargs)
    await component.execute()
    return PromptAction(component)

  def prompt_audio(self, prompt_type, url, **kwargs):
    media_list = [{ 'type': MediaType.AUDIO, 'url': url }]
    return self.prompt(prompt_type=prompt_type, media_list=media_list, **kwargs)

  def prompt_audio_async(self, prompt_type, url, **kwargs):
    media_list = [{ 'type': MediaType.AUDIO, 'url': url }]
    return self.prompt_async(prompt_type=prompt_type, media_list=media_list, **kwargs)

  def prompt_ringtone(self, prompt_type, name, **kwargs):
    media = prepare_prompt_media_list({ 'name': name }, kwargs)
    media['type'] = MediaType.RINGTONE
    return self.prompt(prompt_type=prompt_type, media_list=[media], **kwargs)

  def prompt_ringtone_async(self, prompt_type, name, **kwargs):
    media = prepare_prompt_media_list({ 'name': name }, kwargs)
    media['type'] = MediaType.RINGTONE
    return self.prompt_async(prompt_type=prompt_type, media_list=[media], **kwargs)

  def prompt_tts(self, prompt_type, text, **kwargs):
    media = prepare_prompt_media_list({ 'text': text }, kwargs)
    media['type'] = MediaType.TTS
    return self.prompt(prompt_type=prompt_type, media_list=[media], **kwargs)

  def prompt_tts_async(self, prompt_type, text, **kwargs):
    media = prepare_prompt_media_list({ 'text': text }, kwargs)
    media['type'] = MediaType.TTS
    return self.prompt_async(prompt_type=prompt_type, media_list=[media], **kwargs)

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

  async def send_digits(self, digits):
    component = SendDigits(self, digits)
    await component.wait_for(CallSendDigitsState.FINISHED)
    return SendDigitsResult(component)

  async def send_digits_async(self, digits):
    component = SendDigits(self, digits)
    await component.execute()
    return SendDigitsAction(component)

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

  async def fax_receive(self):
    component = FaxReceive(self)
    await component.wait_for(CallFaxState.ERROR, CallFaxState.FINISHED)
    return FaxResult(component)

  async def fax_receive_async(self):
    component = FaxReceive(self)
    await component.execute()
    return FaxAction(component)

  async def fax_send(self, url, identity=None, header=None):
    component = FaxSend(self, document=url, identity=identity, header=header)
    await component.wait_for(CallFaxState.ERROR, CallFaxState.FINISHED)
    return FaxResult(component)

  async def fax_send_async(self, url, identity=None, header=None):
    component = FaxSend(self, document=url, identity=identity, header=header)
    await component.execute()
    return FaxAction(component)

  async def tap(self, audio_direction, target_type, target_addr=None, target_port=None, target_ptime=None, target_uri=None, rate=None, codec=None):
    component = Tap(self, audio_direction, target_type, target_addr, target_port, target_ptime, target_uri, rate, codec)
    await component.wait_for(CallTapState.FINISHED)
    return TapResult(component)

  async def tap_async(self, audio_direction, target_type, target_addr=None, target_port=None, target_ptime=None, target_uri=None, rate=None, codec=None):
    component = Tap(self, audio_direction, target_type, target_addr, target_port, target_ptime, target_uri, rate, codec)
    await component.execute()
    return TapAction(component)

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
