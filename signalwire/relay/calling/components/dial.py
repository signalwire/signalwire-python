from signalwire.relay.calling.components import BaseComponent
from ..constants import Method, Notification, CallState
from ...event import Event

class Dial(BaseComponent):
  def __init__(self, call):
    super().__init__(call)
    self.control_id = call.tag

  @property
  def event_type(self):
    return Notification.STATE

  @property
  def method(self):
    return Method.BEGIN

  @property
  def payload(self):
    return {
      'tag': self.call.tag,
      'device': self.call.device
    }

  def notification_handler(self, params):
    self.state = params.get('call_state', None)
    if self.state is None:
      return

    if self.state in self._events_to_await:
      self.unregister()
      self.completed = True
      self.successful = self.state == CallState.ANSWERED
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
