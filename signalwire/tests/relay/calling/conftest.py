import pytest

@pytest.fixture(scope='module')
def relay_client():
  from signalwire.relay.client import Client
  from signalwire.tests import MockedConnection
  return Client(project='project', token='token', connection=MockedConnection)

@pytest.fixture(scope='module')
def relay_calling(relay_client):
  from signalwire.relay.calling import Calling
  return Calling(relay_client)
