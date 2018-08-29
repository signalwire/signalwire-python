from unittest import TestCase


class TestConfigurable(TestCase):
  def test_is_string(self):
    from signalwire.rest import Client as signalwire_client
    client = signalwire_client('account', 'token', signalwire_base_url = 'api.signalwire.com').create
    self.assertEqual(client.api.base_url, 'api.signalwire.com')
