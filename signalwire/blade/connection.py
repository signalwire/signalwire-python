import asyncio
import signal
import aiohttp
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect

class Connection:
    def __init__(self, client):
        self.client = client
        self.host = 'wss://relay.swire.io'
        self.ws_client = None

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.host) as ws:
                print('WS OPENED!')
                self.ws_client = ws
                await self.client.on_socket_open()
                async for msg in ws:
                    print(msg.data)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        inbound = Message.from_json(msg.data)
                        # print(inbound)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print('WebSocket Closed!')
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print('WebSocket Error!')
                        break

    async def close(self):
        await self.ws_client.close()

    async def send(self, message):
        if self.ws_client is not None:
            await self.ws_client.send_str(message.to_json())
        else:
            print('ws_client not ready!')
