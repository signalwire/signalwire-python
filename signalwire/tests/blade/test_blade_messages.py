from unittest import TestCase
from unittest.mock import patch
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect

class TestBladeMessages(TestCase):
  def test_from_json_with_result(self):
    j_string = '{"jsonrpc":"2.0","id":"c0b3cabb-e7f8-445d-b3eb-49add1519300","result":{"protocol":"signalwire_xxx","command":"add","subscribe_channels":["notifications"]}}'
    msg = Message.from_json(j_string)

    self.assertEqual(msg.id, 'c0b3cabb-e7f8-445d-b3eb-49add1519300')
    self.assertEqual(msg.result['protocol'], 'signalwire_xxx')
    self.assertEqual(msg.result['subscribe_channels'], ['notifications'])

  def test_from_json_with_error(self):
    j_string = '{"jsonrpc":"2.0","id":"9ca3c540-e622-420a-a975-58d0abd54abc","error":{"code":-32002,"message":"error description"}}'
    msg = Message.from_json(j_string)

    self.assertEqual(msg.id, '9ca3c540-e622-420a-a975-58d0abd54abc')
    self.assertEqual(msg.error['code'], -32002)
    self.assertEqual(msg.error['message'], 'error description')

  def test_from_json_with_params(self):
    j_string = '{"jsonrpc":"2.0","id":"a691b004-1fc7-4e88-8428-9f1bfed6bf96","method":"blade.broadcast","params":{"event":"relay.test"}}'
    msg = Message.from_json(j_string)

    self.assertEqual(msg.id, 'a691b004-1fc7-4e88-8428-9f1bfed6bf96')
    self.assertEqual(msg.params['event'], 'relay.test')
    self.assertEqual(msg.method, 'blade.broadcast')

  def test_to_json(self):
    msg = Message(params={'test': 'hello world!'})
    msg.id = 'mocked'

    self.assertEqual(msg.to_json(), '{"jsonrpc":"2.0","id":"mocked","params":{"test":"hello world!"}}')

  def test_connect(self):
    msg = Connect(project='project', token='token')
    msg.id = 'mocked'

    self.assertEqual(msg.method, 'blade.connect')
    self.assertEqual(msg.params['authentication']['project'], 'project')
    self.assertEqual(msg.params['authentication']['token'], 'token')
    self.assertEqual(msg.to_json(), '{"method":"blade.connect","jsonrpc":"2.0","id":"mocked","params":{"version":{"major":2,"minor":4,"revision":0},"authentication":{"project":"project","token":"token"}}}')

  def test_connect_kwargs(self):
    msg = Connect(token='token', project='project')
    msg.id = 'mocked'
    self.assertEqual(msg.to_json(), '{"method":"blade.connect","jsonrpc":"2.0","id":"mocked","params":{"version":{"major":2,"minor":4,"revision":0},"authentication":{"project":"project","token":"token"}}}')

  # def test_api_url_scheme(self):
  #   from signalwire.rest import Client as signalwire_client
  #   client = signalwire_client('account', 'token', signalwire_space_url = 'https://myname.signalwire.com')

  #   self.assertEqual(client.api.base_url, 'https://myname.signalwire.com')

  # def test_api_url_environnment(self):
  #   from signalwire.rest import Client as signalwire_client
  #   os.environ['SIGNALWIRE_SPACE_URL'] = 'myname.signalwire.com'
  #   client = signalwire_client('account', 'token')

  #   self.assertEqual(client.api.base_url, 'https://myname.signalwire.com')
