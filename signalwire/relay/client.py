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
  def __init__(self, project, token, host='relay.swire.io'):
    self.loop = asyncio.get_event_loop()
    self.host = host
    self.project = project
    self.token = token
    self.attach_signals()
    self.connection = Connection(self)
    self.uuid = str(uuid4())
    self._reconnect = True
    self.session_id = None
    self.signature = None
    self.protocol = None
    logging.basicConfig(level=logging.DEBUG)

  @property
  def connected(self):
    return isinstance(self.connection, Connection) and self.connection.connected

  def execute(self, message):
    pass

  def connect(self):
    self._reconnect = True
    self.loop.create_task(self._connect())
    self.loop.run_forever()

  async def _connect(self):
    sleep = False
    while self._reconnect:
      try:
        if sleep == True:
          await asyncio.sleep(5)
        await self.connection.connect()
        asyncio.create_task(self.on_socket_open())
        await self.connection.read()
        logging.info('Connection closed..')
      except aiohttp.client_exceptions.ClientConnectorError:
        logging.warn(f"{self.host} seems down..")
      sleep = True

  async def disconnect(self):
    logging.info('Disconnection..')
    # TODO: handle idle state here
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
      result = await self.connection.send(Connect(project=self.project, token=self.token))
      self.session_id = result['sessionid']
      self.signature = result['authorization']['signature']
      self.protocol = await setup_protocol(self)
      logging.info(self.protocol)
      trigger('ready', self, self.uuid)
    except Exception as error:
      logging.error('Auth error: {0}'.format(str(error)))
      pass

  def on_socket_message(self, message):
    if message.method == 'blade.netcast':
      pass
    elif message.method == 'blade.broadcast':
      logging.info('- - - - - relay broadcast')
      logging.info(message.params)
      logging.info('- - - - - relay broadcast')
