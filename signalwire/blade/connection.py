import asyncio
import signal
import aiohttp
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect
import logging
import json

class Connection:
    def __init__(self, client):
        self.client = client
        self.host = 'wss://relay.swire.io'
        self.ws_client = None

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.host) as ws:
                logging.info('WS OPENED!')
                self.ws_client = ws
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
        await self.ws_client.close()

    async def send(self, message):
        if self.ws_client is not None:
            message_json = message.to_json()
            logging.debug("SEND: " + message_json)
            await self.ws_client.send_str(message_json)
        else:
            print('ws_client not ready!')
