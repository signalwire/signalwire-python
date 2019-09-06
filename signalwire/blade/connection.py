import asyncio
import signal
import aiohttp
import logging
import json
import re
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect

class Connection:
  def __init__(self, client):
    self.client = client
    self.host = self._checkHost(client.host)
    self.ws = None

  @property
  def connected(self):
    return isinstance(self.ws, aiohttp.ClientWebSocketResponse) and self.ws.closed == False

  def _checkHost(self, host):
    protocol = '' if re.match(r"^(ws|wss):\/\/", host) else 'wss://'
    return protocol + host

  async def connect(self):
    async with aiohttp.ClientSession() as session:
      async with session.ws_connect(self.host) as ws:
        logging.info('WS OPENED!')
        self.ws = ws
        await self.client.on_socket_open()
        async for msg in ws:
          logging.debug("RECV: " + msg.data)
          if msg.type == aiohttp.WSMsgType.TEXT:
            inbound = Message.from_json(msg.data)
            # print(inbound)
          elif msg.type == aiohttp.WSMsgType.CLOSED:
            logging.info('WebSocket Closed!')
            break
          elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.info('WebSocket Error!')
            break

  async def close(self):
    if self.connected:
      await self.ws.close()

  async def send(self, message):
    if self.connected:
      logging.debug("SEND: " + message.to_json(indent=2))
      await self.ws.send_str(message.to_json())
    else:
      logging.warn('WebSocket client is not ready!')
