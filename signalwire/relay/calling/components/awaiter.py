from . import BaseComponent
from ..constants import Notification, CallState
from ...event import Event

class Awaiter(BaseComponent):

  def __init__(self, call):
    super().__init__(call)
    self.control_id = call.tag

  @property
  def event_type(self):
    return Notification.STATE

  @property
  def method(self):
    return None

  @property
  def payload(self):
    return None

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
