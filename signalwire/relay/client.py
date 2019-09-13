import asyncio
import logging
import signal
import aiohttp
from uuid import uuid4
from signalwire.blade.connection import Connection
from signalwire.blade.messages.connect import Connect
from signalwire.blade.handler import register, unregister, trigger
from .helpers import setup_protocol

class Client:
  def __init__(self, project, token, host='relay.swire.io', connection=Connection):
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
    self._requests = {}
    logging.basicConfig(level=logging.DEBUG)

  @property
  def connected(self):
    return self.connection.connected

  async def execute(self, message):
    logging.debug('We are on execute:')
    if self.connected == False:
      # TODO: put message in a queue and process it later.
      logging.error('Client is not connected!')
      return False
    self._requests[message.id] = self.loop.create_future()
    await self.connection.send(message)
    return await self._requests[message.id]

  def connect(self):
    # FIXME: make this sleep logic better
    sleep = False
    while self._reconnect:
      try:
        self.loop.run_until_complete(self._connect(sleep))
        logging.info('Connection closed..')
      except aiohttp.client_exceptions.ClientConnectorError:
        logging.warn(f"{self.host} seems down..")
      sleep = True

  async def _connect(self, sleep=False):
    if sleep == True:
      await asyncio.sleep(5)
    await self.connection.connect()
    asyncio.create_task(self.on_socket_open())
    await self.connection.read()

  async def disconnect(self):
    logging.info('Disconnection..')
    self._reconnect = False
    await self.connection.close()
    await self.cancel_pending_tasks()
    logging.info(f"Bye bye!")
    self.loop.stop()

  def on(self, event, callback):
    register(event, callback, self.uuid)
    return self

  def off(self, event, callback=None):
    unregister(event, callback, self.uuid)
    return self

  async def cancel_pending_tasks(self):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logging.info(f"Cancelling {len(tasks)} outstanding tasks..")
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

  def attach_signals(self):
    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
      self.loop.add_signal_handler(s, lambda: asyncio.create_task(self.disconnect()))

  async def on_socket_open(self):
    logging.info('Connection successful!')
    try:
      result = await self.execute(Connect(project=self.project, token=self.token))
      self.session_id = result['sessionid']
      self.signature = result['authorization']['signature']
      self.protocol = await setup_protocol(self)
      logging.info(self.protocol)
      trigger('ready', self, self.uuid)
    except Exception as error:
      logging.error('Auth error: {0}'.format(str(error)))

  def message_handler(self, msg):
    if msg.id not in self._requests:
      return self._on_socket_message(msg)

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

  def _on_socket_message(self, message):
    if message.method == 'blade.netcast':
      pass
    elif message.method == 'blade.broadcast':
      logging.info('- - - - - relay broadcast')
      logging.info(message.params)
      logging.info('- - - - - relay broadcast')
