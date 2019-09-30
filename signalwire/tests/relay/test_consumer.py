import pytest
from signalwire.relay.consumer import Consumer
from signalwire.tests import MockedConnection

class InvalidConsumer(Consumer):
  def setup(self):
    self.Connection = MockedConnection
    self.project = 'project'
    self.token = 'token'

def test_invalid_consumer():
  with pytest.raises(Exception):
    invalid = InvalidConsumer()
    invalid.run()
