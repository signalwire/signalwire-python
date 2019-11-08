from time import time
from unittest import TestCase
from signalwire import __version__
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect
from signalwire.blade.messages.execute import Execute
from signalwire.blade.messages.subscription import Subscription
from signalwire.blade.messages.ping import Ping

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
    self.assertEqual(msg.to_json(), '{{"method":"blade.connect","jsonrpc":"2.0","id":"mocked","params":{{"version":{{"major":{0},"minor":{1},"revision":{2}}},"authentication":{{"project":"project","token":"token"}},"agent":"Python SDK/{3}"}}}}'.format(Connect.MAJOR, Connect.MINOR, Connect.REVISION, __version__))

  def test_connect_kwargs(self):
    msg = Connect(token='token', project='project')
    msg.id = 'mocked'
    self.assertEqual(msg.to_json(), '{{"method":"blade.connect","jsonrpc":"2.0","id":"mocked","params":{{"version":{{"major":{0},"minor":{1},"revision":{2}}},"authentication":{{"project":"project","token":"token"}},"agent":"Python SDK/{3}"}}}}'.format(Connect.MAJOR, Connect.MINOR, Connect.REVISION, __version__))

  def test_execute(self):
    msg = Execute({
      'protocol': 'proto',
      'method': 'py.test',
      'params': {
        'nested': True
      }
    })
    msg.id = 'mocked'

    self.assertEqual(msg.method, 'blade.execute')
    self.assertEqual(msg.to_json(), '{"method":"blade.execute","jsonrpc":"2.0","id":"mocked","params":{"protocol":"proto","method":"py.test","params":{"nested":true}}}')

  def test_subscription(self):
    msg = Subscription({
      'protocol': 'proto',
      'command': 'add',
      'channels': ['notif']
    })
    msg.id = 'mocked'

    self.assertEqual(msg.method, 'blade.subscription')
    self.assertEqual(msg.to_json(), '{"method":"blade.subscription","jsonrpc":"2.0","id":"mocked","params":{"protocol":"proto","command":"add","channels":["notif"]}}')

  def test_ping_without_ts(self):
    msg = Ping()
    msg.id = 'mocked'

    self.assertEqual(msg.method, 'blade.ping')
    self.assertEqual(msg.to_json(), '{"method":"blade.ping","jsonrpc":"2.0","id":"mocked","params":{}}')

  def test_ping_with_ts(self):
    ts = time()
    msg = Ping(ts)
    msg.id = 'mocked'

    self.assertEqual(msg.method, 'blade.ping')
    self.assertEqual(msg.to_json(), f'{{"method":"blade.ping","jsonrpc":"2.0","id":"mocked","params":{{"timestamp":{ts}}}}}')
