from signalwire.relay.calling.components import BaseComponent
from ..helpers import prepare_connect_devices, prepare_media_list
from ..constants import Method, Notification, ConnectState
from ...event import Event

class Connect(BaseComponent):
  def __init__(self, call, devices, ringback=[]):
    super().__init__(call)
    self.control_id = call.tag
    self.devices = prepare_connect_devices(devices, call.from_number, call.timeout)
    self.ringback = prepare_media_list(ringback)

  @property
  def event_type(self):
    return Notification.CONNECT

  @property
  def method(self):
    return Method.CONNECT

  @property
  def payload(self):
    tmp = {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'devices': self.devices
    }
    if len(self.ringback) > 0:
      tmp['ringback'] = self.ringback
    return tmp

  def notification_handler(self, params):
    self.state = params.get('connect_state', None)
    if self.state is None:
      return
    self.completed = self.state != ConnectState.CONNECTING
    if self.completed:
      self.unregister()
      self.successful = self.state == ConnectState.CONNECTED
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
