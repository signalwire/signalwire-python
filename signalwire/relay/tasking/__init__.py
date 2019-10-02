import logging
from signalwire.blade.handler import trigger
from signalwire.relay import BaseRelay

class Tasking(BaseRelay):

  @property
  def service(self):
    return 'tasking'

  def notification_handler(self, notification):
    context = notification['context']
    logging.info(f'Receive task in context: {context}')
    trigger(self.client.protocol, notification['message'], suffix=self.ctx_receive_unique(context))
