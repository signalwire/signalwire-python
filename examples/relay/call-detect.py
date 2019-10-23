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
    dial_result = await self.client.calling.dial(to_number='+1xxx', from_number='+1yyy')
    if dial_result.successful is False:
      logging.info('Outboud call failed.')
      return

    amd = await dial_result.call.amd()
    logging.info(f'AMD Result: {amd.result}')

    if amd.successful and amd.result == 'HUMAN':
      # If we detect a HUMAN, say hello and play an audio file.
      await dial_result.call.play_tts(text='Hey human! How you doing?')
      await dial_result.call.play_audio(url='https://cdn.signalwire.com/default-music/welcome.mp3')

    await dial_result.call.hangup()
    logging.info('Outbound call hanged up!')

  def teardown(self):
    logging.info('Consumer teardown..')

consumer = CustomConsumer()
consumer.run()
