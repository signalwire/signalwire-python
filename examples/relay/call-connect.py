import logging
import os
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.host = 'relay.swire.io'
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
      { 'to_number': '+12135877632', 'timeout': 10 },
      { 'to_number': '+12135877632', 'timeout': 20 }
    ]
    # ringback not supported yet
    # ringback = [ { 'type': 'ringtone', 'name': 'it' } ]
    result = await call.connect(device_list=devices)
    if result.successful:
      print('Call Connected!')
      remote_call = result.call

consumer = CustomConsumer()
consumer.run()
