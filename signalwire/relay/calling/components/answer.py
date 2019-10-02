from . import BaseComponent
from ..constants import Method, Notification, CallState
from ...event import Event

class Answer(BaseComponent):
  def __init__(self, call):
    super().__init__(call)
    self.control_id = call.tag

  @property
  def event_type(self):
    return Notification.STATE

  @property
  def method(self):
    return Method.ANSWER

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id
    }

  def notification_handler(self, params):
    self.state = params.get('call_state', None)
    if self.state is None:
      return

    if self.state in self._events_to_await:
      self.unregister()
      self.completed = True
      self.successful = True
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
