import logging
from signalwire.relay import BaseRelay

class Calling(BaseRelay):
  @property
  def service(self):
    return 'calling'

  def notification_handler(self, notification):
    logging.info('Handle calling notification')
    logging.info(notification)

  def new_call(self, *, type='phone', from_number, to_number, timeout=None):
    logging.info(f'Make {type} call from: {from_number} to: {to_number} - timeout: {timeout}')
    # TODO:

  def dial(self, *, type='phone', from_number, to_number, timeout=None):
    logging.info(f'Make {type} call from: {from_number} to: {to_number} - timeout: {timeout}')
    # TODO:
