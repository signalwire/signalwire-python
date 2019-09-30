import logging
from signalwire.blade.helpers import safe_invoke_callback
from .client import Client
from .constants import Constants

class Consumer:
  def __init__(self, RelayClient=Client, **kwargs):
    self.project = kwargs.pop('project', None)
    self.token = kwargs.pop('token', None)
    self.host = kwargs.pop('host', Constants.HOST)
    self.contexts = kwargs.pop('contexts', [])
    self.RelayClient = RelayClient
    self.client = None

  def setup(self):
    pass

  def ready(self):
    pass

  def teardown(self):
    pass

  def on_incoming_call(self, call):
    pass

  def run(self):
    self.setup()
    # self.check_requirements() TODO:
    self.client = self.RelayClient(project=self.project, token=self.token, host=self.host)
    self.client.on('ready', self._client_ready)
    self.client.connect()
    self.teardown()

  async def _client_ready(self, client):
    await self.client.calling.receive(self.contexts, self.on_incoming_call)
    logging.warn('Client ready to rock!')
    safe_invoke_callback(self.ready)
