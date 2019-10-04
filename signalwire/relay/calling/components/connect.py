from signalwire.relay.calling.components import BaseComponent
from ..constants import Method, Notification, CallState
from ...event import Event

class Connect(BaseComponent):
  def __init__(self, call, devices):
    super().__init__(call)
    self.control_id = call.tag
    # TODO: reduce in here the devices to avoid logic in call.py
    self.devices = devices

  @property
  def event_type(self):
    return Notification.CONNECT

  @property
  def method(self):
    return Method.CONNECT

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'devices': self.devices
    }

  def notification_handler(self, params):
    self.state = params.get('connect_state', None)
    if self.state is None:
      return
    # TODO:
