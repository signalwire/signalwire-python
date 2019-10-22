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
    result = await self.client.calling.dial(from_number='+1xxx', to_number='+1yyy')
    if result.successful:
      logging.info('Start tapping')
      tap = await result.call.tap_async(audio_direction='both', target_type='rtp', target_addr='<IP>', target_port=16394)
      await asyncio.sleep(20)
      logging.info('Stop tapping')
      await tap.stop()
      await result.call.hangup()

  def teardown(self):
    logging.info('Consumer teardown..')

consumer = CustomConsumer()
consumer.run()
