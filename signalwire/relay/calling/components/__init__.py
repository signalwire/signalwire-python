import asyncio
import logging
from abc import ABC, abstractmethod, abstractproperty
from uuid import uuid4
from signalwire.blade.handler import register, unregister
from signalwire.blade.messages.execute import Execute
from ..constants import CallState
from ...event import Event

class BaseComponent(ABC):
  def __init__(self, call):
    self.call = call
    self.control_id = str(uuid4())
    self.state = ''
    self.completed = False
    self.successful = False
    self.event = None
    self._future = None
    self._execute_result = None
    self._events_to_await = []

  @abstractproperty
  def event_type(self):
    pass

  @abstractproperty
  def method(self):
    pass

  @abstractproperty
  def payload(self):
    pass

  @abstractmethod
  def notification_handler(self, params):
    pass

  def register(self):
    register(event=self.event_type, callback=self.notification_handler, suffix=self.control_id)
    check_id = self.call.id if self.call.id else self.call.tag
    register(event=check_id, callback=self.terminate, suffix=CallState.ENDED)

  def unregister(self):
    unregister(event=self.event_type, callback=self.notification_handler, suffix=self.control_id)
    if self.call.id:
      unregister(event=self.call.id, callback=self.terminate, suffix=CallState.ENDED)
    unregister(event=self.call.tag, callback=self.terminate, suffix=CallState.ENDED)

  async def execute(self):
    if self.call.ended == True:
      return self.terminate()
    self.register()
    if self.method is None:
      return
    msg = Execute({
      'protocol': self.call.calling.client.protocol,
      'method': self.method,
      'params': self.payload
    })
    try:
      response = await self.call.calling.client.execute(msg)
      self._execute_result = response.get('result', {})
      return self._execute_result
    except Exception as error:
      logging.error('Relay command failed: {0}'.format(str(error)))
      self.terminate()

  async def wait_for(self, *events):
    self._events_to_await = events
    self._future = asyncio.get_event_loop().create_future()
    await self.execute()
    try:
      await self._future
    except asyncio.CancelledError:
      pass

  def terminate(self, params={}):
    self.unregister()
    self.completed = True
    self.successful = False
    self.state = 'failed'
    if 'call_state' in params:
      self.event = Event(params['call_state'], params)
    if self.has_future():
      self._future.cancel()

  def has_future(self):
    return isinstance(self._future, asyncio.Future)
