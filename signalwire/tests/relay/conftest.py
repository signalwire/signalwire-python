import pytest
from signalwire.tests import MockedConnection

@pytest.fixture(scope='function')
def relay_client():
  from signalwire.relay.client import Client
  return Client(project='project', token='token', connection=MockedConnection)
