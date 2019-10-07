from . import BaseComponent
from ..constants import Method, Notification, CallPlayState
from ...event import Event

class Play(BaseComponent):

  def __init__(self, call, play):
    super().__init__(call)
    # TODO: reduce play
    self.play = play

  @property
  def event_type(self):
    return Notification.PLAY

  @property
  def method(self):
    return Method.PLAY

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'play': self.play
    }

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
