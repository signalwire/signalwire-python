from unittest import TestCase


class TestConfigurable(TestCase):
  def test_api_url(self):
    from signalwire.rest import Client as signalwire_client
    client = signalwire_client('account', 'token', signalwire_base_url = 'myname.signalwire.com')
    self.assertEqual(client.api.base_url, 'myname.signalwire.com')

