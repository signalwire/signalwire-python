import logging
import os
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.project = os.getenv('PROJECT', '')
    self.token = os.getenv('TOKEN', '')
    self.contexts = ['office', 'home']

  async def ready(self):
    logging.info('Consumer Ready')
    result = await self.client.calling.dial(from_number='+1xxx', to_number='+1yyy')
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

  def on_incoming_message(self, message):
    logging.info('on_incoming_message')
    logging.info(message)

  def on_message_state_change(self, message):
    logging.info('on_message_state_change')
    logging.info(message)

consumer = CustomConsumer()
consumer.run()
