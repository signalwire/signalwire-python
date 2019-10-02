from . import BaseComponent
from ..constants import Method, Notification, CallState
from ...event import Event

class Hangup(BaseComponent):
  def __init__(self, call, reason: str):
    super().__init__(call)
    self.control_id = call.tag
    self.reason = reason

  @property
  def event_type(self):
    return Notification.STATE

  @property
  def method(self):
    return Method.END

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'reason': self.reason
    }

  def notification_handler(self, params):
    self.state = params.get('call_state', None)
    if self.state is None:
      return

    if self.state in self._events_to_await:
      self.unregister()
      self.completed = True
      self.successful = self.state == CallState.ENDED
      self.event = Event(self.state, params)
      if 'end_reason' in params:
        self.reason = params['end_reason']
      if self.has_future():
        self._future.set_result(True)
