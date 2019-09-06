import asyncio
import logging
import signal
import aiohttp
from signalwire.blade.connection import Connection
from signalwire.blade.messages.connect import Connect

class Client:
  def __init__(self, project, token, host='relay.swire.io'):
    self.loop = asyncio.get_event_loop()
    self.host = host
    self.project = project
    self.token = token
    self.attach_signals()
    self.connection = Connection(self)
    self._reconnect = False
    logging.basicConfig(level=logging.DEBUG)

  @property
  def connected(self):
    return isinstance(self.connection, Connection) and self.connection.connected

  def execute(self, message):
    pass

  def connect(self):
    self._reconnect = True
    self.loop.run_until_complete(self._connect())

  async def _connect(self):
    sleep = False
    while True:
      if self._reconnect == False:
        break
      try:
        if sleep == True:
          await asyncio.sleep(5)
        await self.connection.connect()
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

  async def cancel_pending_tasks(self):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logging.info(f"Cancelling {len(tasks)} outstanding tasks..")
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks)

  def attach_signals(self):
    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
      self.loop.add_signal_handler(s, lambda: asyncio.create_task(self.disconnect()))

  async def on_socket_open(self):
    logging.info('Connection is open..')
    self._reconnect = True # FIXME: move this after
    connect = Connect(project=self.project, token=self.token)
    await self.connection.send(connect)
