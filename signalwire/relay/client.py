import os
import asyncio
import logging
import signal
import aiohttp
from uuid import uuid4
from signalwire.blade.connection import Connection
from signalwire.blade.messages.connect import Connect
from signalwire.blade.messages.ping import Ping
from signalwire.blade.handler import register, unregister, trigger
from .helpers import setup_protocol
from .calling import Calling
from .tasking import Tasking
from .messaging import Messaging
from .message_handler import handle_inbound_message
from .constants import Constants, WebSocketEvents

class Client:
  PING_DELAY = 10

  def __init__(self, project, token, host=Constants.HOST, connection=Connection):
    self.loop = asyncio.get_event_loop()
    self.host = host
    self.project = project
    self.token = token
    self.attach_signals()
    self.connection = connection(self)
    self.uuid = str(uuid4())
    self._reconnect = True
    self.session_id = None
    self.signature = None
    self.protocol = None
    self.contexts = []
    self._calling = None
    self._tasking = None
    self._messaging = None
    self._requests = {}
    self._idle = False
    self._executeQueue = asyncio.Queue()
    self._pingInterval = None
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(level=log_level)

  @property
  def connected(self):
    return self.connection.connected

  @property
  def calling(self):
    if self._calling is None:
      self._calling = Calling(self)
    return self._calling

  @property
  def tasking(self):
    if self._tasking is None:
      self._tasking = Tasking(self)
    return self._tasking

  @property
  def messaging(self):
    if self._messaging is None:
      self._messaging = Messaging(self)
    return self._messaging

  async def execute(self, message):
    if message.id not in self._requests:
      self._requests[message.id] = self.loop.create_future()

    if self._idle == True or self.connected == False:
      await self._executeQueue.put(message)
    else:
      await self.connection.send(message)
    result = await self._requests[message.id]
    del self._requests[message.id]
    return result

  def connect(self):
    while self._reconnect:
      self.loop.run_until_complete(self._connect())

  async def _connect(self):
    try:
      await self.connection.connect()
      asyncio.create_task(self.on_socket_open())
      await self.connection.read()
      self.on_socket_close()
    except aiohttp.client_exceptions.ClientConnectorError as error:
      trigger(WebSocketEvents.ERROR, error, suffix=self.uuid)
      logging.warn(f"{self.host} seems down..")
    try:
      logging.info('Connection closed..')
      await asyncio.sleep(5)
    except asyncio.CancelledError:
      pass

  async def disconnect(self):
    logging.info('Disconnection..')
    self._idle = True
    self._reconnect = False
    await self.connection.close()
    await self.cancel_pending_tasks()
    logging.info(f"Bye bye!")
    self.loop.stop()

  def on(self, event, callback):
    register(event=event, callback=callback, suffix=self.uuid)
    return self

  def off(self, event, callback=None):
    unregister(event=event, callback=callback, suffix=self.uuid)
    return self

  async def cancel_pending_tasks(self):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logging.info(f"Cancelling {len(tasks)} outstanding tasks..")
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

  def handle_signal(self):
    asyncio.create_task(self.disconnect())

  def attach_signals(self):
    for s in ('SIGHUP', 'SIGTERM', 'SIGINT'):
      try:
        self.loop.add_signal_handler(getattr(signal, s), self.handle_signal)
      except:
        pass

  def on_socket_close(self):
    if self._pingInterval:
      self._pingInterval.cancel()
    self.contexts = []
    trigger(WebSocketEvents.CLOSE, suffix=self.uuid)

  async def on_socket_open(self):
    try:
      self._idle = False
      trigger(WebSocketEvents.OPEN, suffix=self.uuid)
      result = await self.execute(Connect(project=self.project, token=self.token))
      self.session_id = result['sessionid']
      self.signature = result['authorization']['signature']
      self.protocol = await setup_protocol(self)
      await self._clearExecuteQueue()
      self._pong = True
      self.keepalive()
      logging.info('Client connected!')
      trigger(Constants.READY, self, suffix=self.uuid)
    except Exception as error:
      logging.error('Client setup error: {0}'.format(str(error)))
      await self.connection.close()

  def keepalive(self):
    async def send_ping():
      if self._pong is False:
        return await self.connection.close()
      self._pong = False
      await self.execute(Ping())
      self._pong = True
    asyncio.create_task(send_ping())
    self._pingInterval = self.loop.call_later(self.PING_DELAY, self.keepalive)

  async def _clearExecuteQueue(self):
    while True:
      if self._executeQueue.empty():
        break
      message = self._executeQueue.get_nowait()
      asyncio.create_task(self.connection.send(message))

  def message_handler(self, msg):
    trigger(WebSocketEvents.MESSAGE, msg, suffix=self.uuid)
    if msg.id not in self._requests:
      return handle_inbound_message(self, msg)

    if hasattr(msg, 'error'):
      self._set_exception(msg.id, msg.error)
    elif hasattr(msg, 'result'):
      try:
        if msg.result['result']['code'] == '200':
          self._set_result(msg.id, msg.result)
        else:
          self._set_exception(msg.id, msg.result['result'])
      except KeyError: # not a Relay with "result.result.code"
        self._set_result(msg.id, msg.result)

  def _set_result(self, uuid, result):
    self._requests[uuid].set_result(result)

  def _set_exception(self, uuid, error):
    # TODO: replace with a custom exception
    self._requests[uuid].set_exception(Exception(error['message']))
