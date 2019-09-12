import asyncio
import aiohttp
from signalwire.blade.messages.message import Message
import json

class BladeTestServer(aiohttp.test_utils.TestServer):
  def __init__(self, **kwargs):
    self.ws = None
    self.app = aiohttp.web.Application()
    self.app.router.add_route('GET', '/', self.handler)
    super().__init__(self.app, scheme='ws', **kwargs)

  async def handler(self, request):
    self.ws = aiohttp.web.WebSocketResponse()
    await self.ws.prepare(request)

    print(request)
    msg = await self.ws.receive_str()
    # json_dict = json.loads(msg)
    # print(json_dict)
    # res = '{"jsonrpc":"2.0","id":"' + json_dict['id'] +'","result":{"session_restored":false,"sessionid":"87cf6699-7a89-4491-b732-b51144155d46","nodeid":"8c03a06e-b0d8-4e5f-a539-85e07bb99b97","master_nodeid":"00000000-0000-0000-0000-000000000000","authorization":{"project":"78429ef1-283b-4fa9-8ebc-16b59f95bb1f","expires_at":null,"scopes":["calling"],"signature":"4b501cec2c31ea356a28d92513037e042c9ab3216b2c833adbff8d7d9a523bda"},"routes":[],"protocols":[],"subscriptions":[],"authorities":[],"authorizations":[],"accesses":[],"protocols_uncertified":["signalwire"]}}'
    # print(res)
    await self.ws.send_str(msg)
    # await self.ws.close()
    return self.ws

# class BladeTestServer(aiohttp.test_utils.RawTestServer):

  # def __init__(self, **kwargs):
  #   super().__init__(self._handle_request, **kwargs)
  #   self._requests = asyncio.Queue()
  #   self._responses = {}

  # async def close(self):
  #   ''' cancel all pending requests before closing '''
  #   for future in self._responses.values():
  #     future.cancel()
  #   await super().close()

  # async def _handle_request(self, request):
  #   ''' push request to test case and wait until it provides a response '''
  #   ws = aiohttp.web.WebSocketResponse()
  #   await ws.prepare(request)
  #   self._responses[id(request)] = response = asyncio.Future()
  #   self._requests.put_nowait(request)
  #   try:
  #     # wait until test case provides a response
  #     return await response
  #   finally:
  #     del self._responses[id(request)]

  # async def receive_request(self):
  #   ''' wait until test server receives a request '''
  #   return await self._requests.get()

  # def send_response(self, request, *args, **kwargs):
  #   ''' send response from test case to client code '''
  #   response = aiohttp.web.Response(*args, **kwargs)
  #   self._responses[id(request)].set_result(response)
