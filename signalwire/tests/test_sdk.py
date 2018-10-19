from unittest import TestCase

class TestConfigurable(TestCase):
  def test_api_url(self):
    from signalwire.rest import Client as signalwire_client
    client = signalwire_client('account', 'token', signalwire_space_url = 'myname.signalwire.com')

    self.assertEqual(client.api.base_url, 'https://myname.signalwire.com')

  def test_api_url_scheme(self):
    from signalwire.rest import Client as signalwire_client
    client = signalwire_client('account', 'token', signalwire_space_url = 'https://myname.signalwire.com')

    self.assertEqual(client.api.base_url, 'https://myname.signalwire.com')
