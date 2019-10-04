import logging
from signalwire.blade.handler import trigger
from signalwire.relay import BaseRelay
from .message import Message
from .constants import Notification

class Messaging(BaseRelay):

  @property
  def service(self):
    return 'messaging'

  def notification_handler(self, notification):
    notification['params']['event_type'] = notification['event_type']
    message = Message(notification['params'])
    if notification['event_type'] == Notification.STATE:
      trigger(self.client.protocol, message, suffix=self.ctx_state_unique(message.context))
    elif notification['event_type'] == Notification.RECEIVE:
      trigger(self.client.protocol, message, suffix=self.ctx_receive_unique(message.context))

  def send(self, *, call_type='phone', from_number, to_number, timeout=None):
    pass
    # call = Call(calling=self)
    # call.call_type = call_type
    # call.from_number = from_number
    # call.to_number = to_number
    # call.timeout = timeout
    # return call
