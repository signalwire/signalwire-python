from . import BaseComponent
from ..constants import Method, Notification, PromptState
from ..helpers import prepare_collect_params, prepare_media_list
from ...event import Event
from .decorators import stoppable, has_volume_control

@stoppable
@has_volume_control
class Prompt(BaseComponent):

  def __init__(self, call, prompt_type, play, **kwargs):
    super().__init__(call)
    self._collect = prepare_collect_params(prompt_type, kwargs)
    self.play = prepare_media_list(play)
    self.volume_value = kwargs.get('volume', None)
    self.prompt_type = prompt_type
    self.confidence = None
    self.input = None
    self.terminator = None

  @property
  def event_type(self):
    return Notification.COLLECT

  @property
  def method(self):
    return Method.PLAY_AND_COLLECT

  @property
  def payload(self):
    tmp = {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'play': self.play,
      'collect': self._collect,
    }
    if self.volume_value is not None:
      tmp['volume'] = float(self.volume_value)
    return tmp

  def notification_handler(self, params):
    self.completed = True
    self.unregister()
    result = params['result']
    if result['type'] == PromptState.SPEECH:
      self.state = 'successful'
      self.successful = True
      self.input = result['params']['text']
      self.confidence = result['params']['confidence']
    elif result['type'] == PromptState.DIGIT:
      self.state = 'successful'
      self.successful = True
      self.input = result['params']['digits']
      self.terminator = result['params']['terminator']
    else:
      self.state = result['type']
      self.successful = False
    self.prompt_type = result['type']
    self.event = Event(self.prompt_type, result)
    if self.has_future():
      self._future.set_result(True)
