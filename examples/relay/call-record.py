import asyncio
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
    action = await call.record_async(beep=True, terminators='#')
    await asyncio.sleep(10) # Record 10seconds...
    await action.stop()
    print(f"Recording file at: {action.url}")
    await call.hangup()

consumer = CustomConsumer()
consumer.run()
