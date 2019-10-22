from . import BaseComponent
from ..constants import Method, Notification, CallTapState, TapType
from ...event import Event
from .decorators import stoppable

@stoppable
class Tap(BaseComponent):

  def __init__(self, call, audio_direction, target_type, target_addr=None, target_port=None, target_ptime=None, target_uri=None, rate=None, codec=None):
    super().__init__(call)
    self.tap = {
      'type': TapType.AUDIO,
      'params': { 'direction': audio_direction }
    }
    self.device = {
      'type': target_type,
      'params': {}
    }
    if target_addr is not None:
      self.device['params']['addr'] = target_addr
    if target_port is not None:
      self.device['params']['port'] = int(target_port)
    if target_ptime is not None:
      self.device['params']['ptime'] = int(target_ptime)
    if target_uri is not None:
      self.device['params']['uri'] = target_uri
    if rate is not None:
      self.device['params']['rate'] = int(rate)
    if codec is not None:
      self.device['params']['codec'] = codec

  @property
  def event_type(self):
    return Notification.TAP

  @property
  def method(self):
    return Method.TAP

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'tap': self.tap,
      'device': self.device
    }

  @property
  def source_device(self):
    try:
      return self._execute_result['source_device']
    except Exception:
      return {}

  def notification_handler(self, params):
    self.state = params.get('state', None)
    if self.state is None:
      return
    if 'tap' in params:
      self.tap = params['tap']
    if 'device' in params:
      self.device = params['device']

    self.completed = self.state == CallTapState.FINISHED
    if self.completed:
      self.unregister()
      self.successful = True
      self.event = Event(self.state, params)
      if self.has_future():
        self._future.set_result(True)
