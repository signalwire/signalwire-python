from aiohttp import WSMsgType, ClientSession, ClientWebSocketResponse
import logging
import re
from signalwire.blade.messages.message import Message

class Connection:
  def __init__(self, client, session=ClientSession):
    self._session = session()
    self.client = client
    self.host = self._checkHost(client.host)
    self.ws = None
    self._requests = {}

  @property
  def connected(self):
    return self.ws is not None and self.ws.closed == False

  def _checkHost(self, host):
    # TODO: move to a helper
    protocol = '' if re.match(r"^(ws|wss):\/\/", host) else 'wss://'
    return protocol + host

  async def send(self, message):
    logging.debug('SEND: \n' + message.to_json(indent=2))
    await self.ws.send_str(message.to_json())

  async def connect(self):
    logging.debug('Connecting to: {0}'.format(self.host))
    self.ws = await self._session.ws_connect(self.host)

  async def read(self):
    async for msg in self.ws:
      logging.debug('RECV: \n' + msg.data)
      if msg.type == WSMsgType.TEXT:
        self.client.message_handler(Message.from_json(msg.data))
      elif msg.type == WSMsgType.CLOSED:
        logging.info('WebSocket Closed!')
        break
      elif msg.type == WSMsgType.ERROR:
        logging.info('WebSocket Error!')
        break

  async def close(self):
    if self.connected:
      await self.ws.close()
