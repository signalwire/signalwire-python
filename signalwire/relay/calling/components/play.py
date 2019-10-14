from . import BaseComponent
from ..constants import Method, Notification, CallPlayState
from ..helpers import prepare_media_list
from ...event import Event
from .decorators import stoppable, pausable, resumable, has_volume_control

@stoppable
@pausable
@resumable
@has_volume_control
class Play(BaseComponent):

  def __init__(self, call, play, volume=0):
    super().__init__(call)
    self.play = prepare_media_list(play)
    self.volume_value = float(volume)

  @property
  def event_type(self):
    return Notification.PLAY

  @property
  def method(self):
    return Method.PLAY

  @property
  def payload(self):
    tmp = {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'play': self.play
    }
    if self.volume_value != 0:
      tmp['volume'] = self.volume_value
    return tmp

  def notification_handler(self, params):
    self.state = params.get('state', None)
    if self.state is None:
      return

    self.completed = self.state != CallPlayState.PLAYING
    if self.completed:
      self.unregister()
      self.successful = self.state == CallPlayState.FINISHED
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
