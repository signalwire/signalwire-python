import logging
import os
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.project = os.getenv('PROJECT', '')
    self.token = os.getenv('TOKEN', '')
    self.host = 'relay.swire.io'
    self.contexts = ['office', 'home']

  async def ready(self):
    logging.info('Consumer is ready to rock!')

  def teardown(self):
    logging.info('Consumer teardown..')

  async def on_incoming_call(self, call):
    logging.info('on_incoming_call')
    logging.info(call)

consumer = CustomConsumer()
consumer.run()
