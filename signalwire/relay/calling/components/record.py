from . import BaseComponent
from ..constants import Method, Notification, CallRecordState, RecordType
from ..helpers import prepare_record_params
from ...event import Event
from .decorators import stoppable

@stoppable
class Record(BaseComponent):

  def __init__(self, call, record_type=RecordType.AUDIO, beep=None, record_format=None, stereo=None, direction=None, initial_timeout=None, end_silence_timeout=None, terminators=None):
    super().__init__(call)
    self.url = ''
    self.duration = 0
    self.size = 0
    self._record = prepare_record_params(record_type, beep, record_format, stereo, direction, initial_timeout, end_silence_timeout, terminators)

  @property
  def event_type(self):
    return Notification.RECORD

  @property
  def method(self):
    return Method.RECORD

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'record': self._record
    }

  def notification_handler(self, params):
    self.state = params.get('state', None)
    if self.state is None:
      return

    self.completed = self.state != CallRecordState.RECORDING
    if self.completed:
      self.unregister()
      self.successful = self.state == CallRecordState.FINISHED
      self.event = Event(self.state, params)
      self.url = params.get('url', '')
      self.duration = params.get('duration', 0)
      self.size = params.get('size', 0)
      if self.has_future():
        self._future.set_result(True)
