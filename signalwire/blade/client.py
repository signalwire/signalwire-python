import asyncio
import signal
import aiohttp
from signalwire.blade.connection import Connection
from signalwire.blade.messages.connect import Connect

class Client:
    def __init__(self, project, token):
        self.loop = asyncio.get_event_loop()
        self.project = project
        self.token = token
        self.connection = None
        self.attach_signals()

    def connect(self):
        self.connection = Connection(self)
        self.loop.run_until_complete(self.connection.connect())
        print('Connection closed..')

        # task = self.loop.create_task(self.connection.connect())
        # task.add_done_callback(self.on_socket_close)
        # self.loop.add_signal_handler(signal.SIGINT, self.shutdown)
        # self.loop.run_forever()
        # try:
        #     self.loop.run_until_complete(main_task)
        #     pass
        # except asyncio.CancelledError:
        #     print('CancelledError?')
        # self.loop.close()

    async def disconnect(self):
      print('Disconnect from socket...')
      await self.connection.close()

    def attach_signals(self):
      for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
          self.loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self.shutdown(s)))

    async def shutdown(self, signal):
        print(f"Received exit signal {signal.name}")
        await self.disconnect()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        print(f"Cancelling {len(tasks)} outstanding tasks..")
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks)
        print(f"Bye bye!")
        self.loop.stop()

    async def on_socket_open(self):
      connect = Connect(project=self.project, token=self.token)
      await self.connection.send(connect)

    def on_socket_close(self, task):
        print('Socket closed?')
        print(task.exception())
        pass

    def execute(self, message):
        print('Execute message')
        pass
