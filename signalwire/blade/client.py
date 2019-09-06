import asyncio
import signal
import aiohttp
from signalwire.blade.connection import Connection
from signalwire.blade.messages.connect import Connect
import logging

class Client:
    def __init__(self, project, token):
      self.loop = asyncio.get_event_loop()
      self.project = project
      self.token = token
      self.connection = None
      self.attach_signals()
      self.connected = False
      self.reconnect = False
      logging.basicConfig(level=logging.DEBUG)

    def connect(self):
      self.connection = Connection(self)
      self.loop.run_until_complete(self.connection.connect())
      logging.info('Connection closed..')
      self.connected = True

    async def disconnect(self):
      self.connected = False
      self.reconnect = False
      logging.info('Disconnect from socket...')
      await self.connection.close()

    def attach_signals(self):
      for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        self.loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self.shutdown(s)))

    async def shutdown(self, signal):
      logging.info(f"Received exit signal {signal.name}")
      await self.disconnect()
      tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
      logging.info(f"Cancelling {len(tasks)} outstanding tasks..")
      [task.cancel() for task in tasks]
      await asyncio.gather(*tasks)
      logging.info(f"Bye bye!")
      self.loop.stop()

    async def on_socket_open(self):
      logging.info('Connection is open.')
      self.connected = True
      self.reconnect = True
      connect = Connect(project=self.project, token=self.token)
      await self.connection.send(connect)

    def on_socket_close(self, task):
      logging.info('Socket closed?')
      print(task.exception())
      pass

    def execute(self, message):
      pass
