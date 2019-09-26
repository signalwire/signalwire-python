from abc import ABC, abstractmethod, abstractproperty
import logging
from signalwire.blade.handler import register
from .helpers import receive_contexts

class BaseRelay(ABC):
  def __init__(self, client):
    self.client = client

  @abstractproperty
  def service(self):
    pass

  @abstractmethod
  def notification_handler(self, notification):
    pass

  def ctx_receive_unique(self, context):
    return f"{self.service}.ctx_receive.{context}"

  async def receive(self, contexts, handler):
    try:
      logging.info(f'Trying to receive contexts: {contexts}')
      await receive_contexts(self.client, contexts)
      for context in contexts:
        register(self.client.protocol, handler, self.ctx_receive_unique(context))
    except Exception as error:
      logging.error('receive error: {0}'.format(str(error)))
