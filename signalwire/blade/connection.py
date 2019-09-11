from aiohttp import WSMsgType, ClientSession, ClientWebSocketResponse
import logging
import re
from signalwire.blade.messages.message import Message

class Connection:
  def __init__(self, client, session=ClientSession()):
    self._session = session
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
    if msg.id not in self._requests:
      return self.client.on_socket_message(msg)

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


  async def connect(self):
    logging.debug('Connecting to: {0}'.format(self.host))
    self.ws = await self._session.ws_connect(self.host)

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
