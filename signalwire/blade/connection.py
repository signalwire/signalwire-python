import asyncio
import signal
from aiohttp import WSMsgType, ClientSession, ClientWebSocketResponse
import logging
import json
import re
from signalwire.blade.messages.message import Message

class Connection(ClientSession):
  def __init__(self, client):
    super().__init__()
    self.client = client
    self.host = self._checkHost(client.host)
    self.ws = None
    self._requests = {}

  @property
  def connected(self):
    return isinstance(self.ws, ClientWebSocketResponse) and self.ws.closed == False

  def _checkHost(self, host):
    protocol = '' if re.match(r"^(ws|wss):\/\/", host) else 'wss://'
    return protocol + host

  def set_result(self, uuid, result):
    self._requests[uuid].set_result(result)

  def set_exception(self, uuid, error):
    # TODO: replace with a custom exception
    self._requests[uuid].set_exception(Exception(error['message']))

  def message_handler(self, msg):
    if msg.id in self._requests:
      if hasattr(msg, 'error'):
        self.set_exception(msg.id, msg.error)
      elif hasattr(msg, 'result'):
        try:
          if msg.result['result']['code'] == '200':
            self.set_result(msg.id, msg.result)
          else:
            self.set_exception(msg.id, msg.result['result'])
        except KeyError: # not a Relay with "result.result.code"
          self.set_result(msg.id, msg.result)
    else:
      # TODO: dispatch inbound message to the client
      logging.info('Inbound msg:')
      print(msg)

  async def connect(self):
    logging.debug('Connecting to: {0}'.format(self.host))
    self.ws = await self.ws_connect(self.host)

  async def read(self):
    async for msg in self.ws:
      logging.debug('RECV: \n' + msg.data)
      if msg.type == WSMsgType.TEXT:
        self.message_handler(Message.from_json(msg.data))
      elif msg.type == WSMsgType.CLOSED:
        logging.info('WebSocket Closed!')
        break
      elif msg.type == WSMsgType.ERROR:
        logging.info('WebSocket Error!')
        break

  async def close(self):
    if self.connected:
      await self.ws.close()

  async def send(self, message):
    if self.connected == False:
      logging.warn('WebSocket client is not ready!')
      return False
    self._requests[message.id] = self.client.loop.create_future()
    logging.debug('SEND: \n' + message.to_json(indent=2))
    await self.ws.send_str(message.to_json())
    return await self._requests[message.id]
