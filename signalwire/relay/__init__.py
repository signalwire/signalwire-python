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

  def ctx_state_unique(self, context):
    return f"{self.service}.ctx_state.{context}"

  async def receive(self, contexts, handler):
    try:
      await receive_contexts(self.client, contexts)
      for context in contexts:
        register(event=self.client.protocol, callback=handler, suffix=self.ctx_receive_unique(context))
    except Exception as error:
      logging.error('receive error: {0}'.format(str(error)))

  async def state_change(self, contexts, handler):
    try:
      await receive_contexts(self.client, contexts)
      for context in contexts:
        register(event=self.client.protocol, callback=handler, suffix=self.ctx_state_unique(context))
    except Exception as error:
      logging.error('state_change error: {0}'.format(str(error)))
