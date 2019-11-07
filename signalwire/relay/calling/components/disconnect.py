from signalwire.relay.calling.components import BaseComponent
from ..constants import Method, Notification, ConnectState
from ...event import Event

class Disconnect(BaseComponent):
  def __init__(self, call):
    super().__init__(call)
    self.control_id = call.tag

  @property
  def event_type(self):
    return Notification.CONNECT

  @property
  def method(self):
    return Method.DISCONNECT

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id
    }

  def notification_handler(self, params):
    self.state = params.get('connect_state', None)
    if self.state is None:
      return
    self.completed = self.state != ConnectState.CONNECTING
    if self.completed:
      self.unregister()
      self.successful = self.state == ConnectState.DISCONNECTED
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
