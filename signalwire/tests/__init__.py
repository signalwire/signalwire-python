import asyncio
from unittest.mock import MagicMock
from signalwire.blade.messages.message import Message

def AsyncMock(*args, **kwargs):
  m = MagicMock(*args, **kwargs)

  async def mock_coro(*args, **kwargs):
    return m(*args, **kwargs)

  mock_coro.mock = m
  return mock_coro

class MockedConnection:
  def __init__(self, client):
    self.client = client
    self.connect = AsyncMock()
    self.queue = asyncio.Queue()
    self.responses = []
    self.close = AsyncMock()
    self.connected = True

  async def send(self, message):
    await self.queue.put(message.id)

  async def read(self):
    for response in self.responses:
      msg = Message.from_json(response)
      msg.id = await self.queue.get()
      self.client.message_handler(msg)
