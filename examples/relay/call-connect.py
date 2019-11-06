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

  def teardown(self):
    logging.info('Consumer teardown..')

  async def on_incoming_call(self, call):
    await call.answer()
    devices = [
      { 'to_number': '+1xxx', 'timeout': 10 },
      { 'to_number': '+1yyy', 'timeout': 20 }
    ]
    ringback = [
      { 'type': 'ringtone', 'name': 'us' }
    ]
    result = await call.connect(device_list=devices, ringback_list=ringback)
    if result.successful:
      print('Call Connected!')
      remote_call = result.call

consumer = CustomConsumer()
consumer.run()
