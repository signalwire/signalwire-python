import logging
from signalwire.blade.handler import trigger
from signalwire.relay import BaseRelay
from .call import Call
from .constants import Notification, DetectState, ConnectState

class Calling(BaseRelay):
  def __init__(self, client):
    super().__init__(client)
    self.calls = []

  @property
  def service(self):
    return 'calling'

  def notification_handler(self, notification):
    notification['params']['event_type'] = notification['event_type']
    if notification['event_type'] == Notification.STATE:
      self._on_state(notification['params'])
    elif notification['event_type'] == Notification.RECEIVE:
      self._on_receive(notification['params'])
    elif notification['event_type'] == Notification.CONNECT:
      self._on_connect(notification['params'])
    elif notification['event_type'] == Notification.PLAY:
      self._on_play(notification['params'])
    elif notification['event_type'] == Notification.COLLECT:
      self._on_collect(notification['params'])
    elif notification['event_type'] == Notification.RECORD:
      self._on_record(notification['params'])
    elif notification['event_type'] == Notification.FAX:
      self._on_fax(notification['params'])
    elif notification['event_type'] == Notification.SEND_DIGITS:
      self._on_send_digits(notification['params'])
    elif notification['event_type'] == Notification.TAP:
      self._on_tap(notification['params'])
    elif notification['event_type'] == Notification.DETECT:
      self._on_detect(notification['params'])

  def new_call(self, *, call_type='phone', from_number, to_number, timeout=None):
    call = Call(calling=self)
    call.call_type = call_type
    call.from_number = from_number
    call.to_number = to_number
    call.timeout = timeout
    return call

  async def dial(self, *, call_type='phone', from_number, to_number, timeout=None):
    call = Call(calling=self)
    call.call_type = call_type
    call.from_number = from_number
    call.to_number = to_number
    call.timeout = timeout
    return await call.dial()

  def add_call(self, call):
    self.calls.append(call)

  def remove_call(self, call):
    try:
      self.calls.remove(call)
    except ValueError:
      logging.warn('Call to remove not found')

  def _get_call_by_id(self, call_id):
    for call in self.calls:
      if call.id == call_id:
        return call
    return None

  def _get_call_by_tag(self, tag):
    for call in self.calls:
      if call.tag == tag:
        return call
    return None

  def _on_state(self, params):
    call = self._get_call_by_id(params['call_id'])
    tag = params.get('tag', None)
    if call is None and tag is not None:
      call = self._get_call_by_tag(tag)

    if call is not None:
      if call.id is None:
        call.id = params['call_id']
        call.node_id = params['node_id']
      trigger(Notification.STATE, params, suffix=call.tag) # Notify components listening on State and Tag
      call._state_changed(params)
    elif 'call_id' in params and 'peer' in params:
      call = Call(calling=self, **params)
    else:
      logging.error('Unknown call {0}'.format(params['call_id']))

  def _on_receive(self, params):
    call = Call(calling=self, **params)
    trigger(self.client.protocol, call, suffix=self.ctx_receive_unique(call.context))

  def _on_connect(self, params):
    call = self._get_call_by_id(params['call_id'])
    state = params['connect_state']
    if call is not None:
      try:
        if state == ConnectState.CONNECTED:
          call.peer = self._get_call_by_id(params['peer']['call_id'])
        else:
          call.peer = None
      except KeyError:
        pass
      trigger(Notification.CONNECT, params, suffix=call.tag) # Notify components listening on Connect and Tag
      trigger(call.tag, params, suffix='connect.stateChange')
      trigger(call.tag, params, suffix=f"connect.{state}")

  def _on_play(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.PLAY, params, suffix=params['control_id']) # Notify components listening on Play and control_id
      trigger(call.tag, params, suffix='play.stateChange')
      trigger(call.tag, params, suffix=f"play.{params['state']}")

  def _on_collect(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.COLLECT, params, suffix=params['control_id']) # Notify components listening on Collect and control_id
      trigger(call.tag, params, suffix='prompt')

  def _on_record(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.RECORD, params, suffix=params['control_id']) # Notify components listening on Record and control_id
      trigger(call.tag, params, suffix='record.stateChange')
      trigger(call.tag, params, suffix=f"record.{params['state']}")

  def _on_fax(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.FAX, params, suffix=params['control_id']) # Notify components listening on Fax and control_id
      trigger(call.tag, params, suffix='fax.stateChange')
      try:
        trigger(call.tag, params, suffix=f"fax.{params['fax']['type']}")
      except KeyError:
        pass

  def _on_send_digits(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.SEND_DIGITS, params, suffix=params['control_id']) # Notify components listening on SendDigits and control_id
      trigger(call.tag, params, suffix='sendDigits.stateChange')
      trigger(call.tag, params, suffix=f"sendDigits.{params['state']}")

  def _on_tap(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.TAP, params, suffix=params['control_id']) # Notify components listening on Tap and control_id
      trigger(call.tag, params, suffix='tap.stateChange')
      trigger(call.tag, params, suffix=f"tap.{params['state']}")

  def _on_detect(self, params):
    call = self._get_call_by_id(params['call_id'])
    if call is not None:
      trigger(Notification.DETECT, params, suffix=params['control_id']) # Notify components listening on Detect and control_id
      try:
        event = params['detect']['params']['event']
        suffix = event if event == DetectState.FINISHED or event == DetectState.ERROR else 'update'
        trigger(call.tag, params['detect'], suffix=f"detect.{suffix}")
      except KeyError:
        pass
