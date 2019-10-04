import asyncio
import pytest
from signalwire.tests import MockedConnection, AsyncMock

@pytest.fixture(scope='function')
def relay_client(event_loop):
  from signalwire.relay.client import Client
  client = Client(project='project', token='token', connection=MockedConnection)
  client.loop = event_loop
  return client

@pytest.fixture(scope='function')
def relay_client_to_connect(relay_client):
  asyncio.sleep = AsyncMock() # Mock sleep
  relay_client.connection.responses = [
    '{"jsonrpc":"2.0","id":"uuid","result":{"session_restored":false,"sessionid":"87cf6699-7a89-4491-b732-b51144155d46","nodeid":"uuid_node","master_nodeid":"00000000-0000-0000-0000-000000000000","authorization":{"project":"project","expires_at":null,"scopes":["calling"],"signature":"random_signature"},"routes":[],"protocols":[],"subscriptions":[],"authorities":[],"authorizations":[],"accesses":[],"protocols_uncertified":["signalwire"]}}',
    '{"jsonrpc":"2.0","id":"uuid","result":{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"protocol":"signalwire_random_proto"}}}',
    '{"jsonrpc":"2.0","id":"uuid","result":{"protocol":"signalwire_random_proto","command":"add","subscribe_channels":["notifications"]}}'
  ]
  return relay_client
