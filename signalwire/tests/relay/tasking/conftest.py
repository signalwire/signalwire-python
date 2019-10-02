import json
import pytest
from signalwire.tests import MockedConnection, AsyncMock

@pytest.fixture(scope='function')
def relay_tasking(relay_client):
  relay_client.protocol = 'signalwire-proto-test'
  response = json.loads('{"requester_nodeid":"uuid","responder_nodeid":"uuid","result":{"code":"200","message":"Receiving all inbound related to the requested relay contexts and available scopes"}}')
  relay_client.execute = AsyncMock(return_value=response)
  return relay_client.tasking
