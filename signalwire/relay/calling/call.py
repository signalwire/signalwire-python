from uuid import uuid4
from .constants import CallState, DisconnectReason
from .components.dial import Dial
from .components.hangup import Hangup
from .components.answer import Answer
from .results.dial_result import DialResult
from .results.hangup_result import HangupResult
from .results.answer_result import AnswerResult

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

  def _state_changed(self, params):
    self.prev_state = self.state
    self.state = params['call_state']
    if self.state == CallState.ENDED:
      # TODO: terminate components
      end_reason = params.get('end_reason', '')
      self.failed = end_reason == DisconnectReason.ERROR
      self.busy = end_reason == DisconnectReason.BUSY
      self.calling.remove_call(self)
