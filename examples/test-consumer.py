import logging
import os
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.project = os.getenv('PROJECT', '')
    self.token = os.getenv('TOKEN', '')
    self.contexts = ['office', 'home']

  async def ready(self):
    result = await self.client.calling.dial(from_number='+12075699736', to_number='+12044000543')
    if result.successful:
      logging.info('Call answered')

  def teardown(self):
    logging.info('Consumer teardown..')

  async def on_incoming_call(self, call):
    result = await call.answer()
    if result.successful:
      logging.info('Call answered')

  async def on_task(self, message):
    logging.info('Handle inbound task')
    logging.info(message)

consumer = CustomConsumer()
consumer.run()
