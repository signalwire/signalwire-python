import logging
from signalwire.blade.messages.execute import Execute
from signalwire.blade.handler import trigger
from signalwire.relay import BaseRelay
from .message import Message
from .send_result import SendResult
from .constants import Notification, Method

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

  async def send(self, *, from_number, to_number, context, body=None, media=None, tags=None):
    params = {
      'from_number': from_number,
      'to_number': to_number,
      'context': context
    }
    if body:
      params['body'] = body
    if media:
      params['media'] = media
    if tags:
      params['tags'] = tags

    message = Execute({
      'protocol': self.client.protocol,
      'method': Method.SEND,
      'params': params
    })
    try:
      response = await self.client.execute(message)
      logging.info(response['result']['message'])
      return SendResult(response['result'])
    except Exception as error:
      logging.error(f'Messaging send error: {str(error)}')
      return SendResult()
