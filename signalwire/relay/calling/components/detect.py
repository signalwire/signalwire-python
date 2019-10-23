from . import BaseComponent
from ..constants import Method, Notification, DetectState, DetectType
from ...event import Event
from .decorators import stoppable

@stoppable
class Detect(BaseComponent):

  def __init__(self, call, detect_type, wait_for_beep=False, timeout=None, initial_timeout=None, end_silence_timeout=None, machine_voice_threshold=None, machine_words_threshold=None, tone=None, digits=None):
    super().__init__(call)
    self.detect_type = detect_type
    params = {}
    if initial_timeout is not None:
      params['initial_timeout'] = initial_timeout
    if end_silence_timeout is not None:
      params['end_silence_timeout'] = end_silence_timeout
    if machine_voice_threshold is not None:
      params['machine_voice_threshold'] = machine_voice_threshold
    if machine_words_threshold is not None:
      params['machine_words_threshold'] = machine_words_threshold
    if tone is not None:
      params['tone'] = tone
    if digits is not None:
      params['digits'] = digits
    self.detect = {
      'type': self.detect_type,
      'params': params
    }
    self.timeout = timeout
    self._wait_for_beep = wait_for_beep
    self._waiting_for_ready = False
    self.result = None
    self._results = []

  @property
  def event_type(self):
    return Notification.DETECT

  @property
  def method(self):
    return Method.DETECT

  @property
  def payload(self):
    tmp = {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'detect': self.detect
    }
    if self.timeout:
      tmp['timeout'] = self.timeout
    return tmp

  def notification_handler(self, params):
    try:
      detect = params['detect']
      self.detect_type = detect['type']
      self.state = detect['params']['event']
    except KeyError:
      return

    if self.state in [DetectState.FINISHED, DetectState.ERROR]:
      return self._complete(detect)

    if not self.has_future():
      self._results.append(self.state)
      return

    if self.detect_type == DetectType.DIGIT:
      return self._complete(detect)

    if self._waiting_for_ready:
      if self.state == DetectState.READY:
        return self._complete(detect)
      return

    if self._wait_for_beep and self.state == DetectState.MACHINE:
      self._waiting_for_ready = True
      return

    if self.state in self._events_to_await:
      return self._complete(detect)

  def _complete(self, detect):
    self.unregister()
    self.completed = True
    self.event = Event(self.state, detect)
    if self.has_future():
      # force READY/NOT_READY to MACHINE
      self.result = DetectState.MACHINE if self.state in [DetectState.READY, DetectState.NOT_READY] else self.state
      self.successful = self.state not in [DetectState.FINISHED, DetectState.ERROR]
      self._future.set_result(True)
    else:
      self.result = ','.join(self._results)
      self.successful = self.state != DetectState.ERROR
