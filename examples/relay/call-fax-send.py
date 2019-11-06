import logging
import os
from signalwire.relay.consumer import Consumer

class Sender(Consumer):
  def setup(self):
    self.project = os.getenv('PROJECT', '')
    self.token = os.getenv('TOKEN', '')
    self.contexts = ['default']

  async def ready(self):
    logging.info('Sender Ready')
    dial_result = await self.client.calling.dial(to_number='+1xxx', from_number='+1yyy')
    if dial_result.successful is False:
      logging.info('Outboud call failed.')
      return

    fax = await dial_result.call.fax_send(url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', header='Custom Header')
    logging.info(f'Send fax Result: {fax.document} with pages {fax.pages}')

    await dial_result.call.hangup()
    logging.info('Outbound call completed!')

  def teardown(self):
    logging.info('Consumer teardown..')

s = Sender()
s.run()
