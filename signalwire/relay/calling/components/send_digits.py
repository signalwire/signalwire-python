from . import BaseComponent
from ..constants import Method, Notification, CallSendDigitsState
from ...event import Event

class SendDigits(BaseComponent):

  def __init__(self, call, digits):
    super().__init__(call)
    self.digits = digits

  @property
  def event_type(self):
    return Notification.SEND_DIGITS

  @property
  def method(self):
    return Method.SEND_DIGITS

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'digits': self.digits
    }

  def notification_handler(self, params):
    self.state = params.get('state', None)
    if self.state is None:
      return

    self.completed = self.state == CallSendDigitsState.FINISHED
    self.successful = self.completed
    self.unregister()
    self.event = Event(self.state, params)
    if self.has_future():
      self._future.set_result(True)
