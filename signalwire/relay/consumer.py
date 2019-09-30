import logging
from signalwire.blade.helpers import safe_invoke_callback
from .client import Client
from .constants import Constants

class Consumer:
  def __init__(self, **kwargs):
    self.project = kwargs.pop('project', None)
    self.token = kwargs.pop('token', None)
    self.host = kwargs.pop('host', Constants.HOST)
    self.contexts = kwargs.pop('contexts', [])
    self.Connection = kwargs.pop('Connection', None)
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
    self.check_requirements()
    self.client = Client(**self._build_relay_client_params())
    self.client.on('ready', self._client_ready)
    self.client.connect()
    self.teardown()

  def check_requirements(self):
    if self.project is None or self.token is None or len(self.contexts) <= 0:
      raise Exception('project, token and contexts instance attributes are required!')

  def _build_relay_client_params(self):
    params = {
      'project': self.project,
      'token': self.token
    }
    if self.host is not None:
      params['host'] = self.host
    if self.Connection is not None:
      params['connection'] = self.Connection
    return params

  async def _client_ready(self, client):
    await self.client.calling.receive(self.contexts, self.on_incoming_call)
    logging.warn('Client ready to rock!')
    safe_invoke_callback(self.ready)
