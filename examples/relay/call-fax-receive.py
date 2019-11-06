import logging
import os
from signalwire.relay.consumer import Consumer

class Receiver(Consumer):
  def setup(self):
    self.project = os.getenv('PROJECT', '')
    self.token = os.getenv('TOKEN', '')
    self.contexts = ['office', 'home']

  async def on_incoming_call(self, call):
    await call.answer()
    fax = await call.fax_receive()
    print(f"Fax received: {fax.document}")
    await call.hangup()

r = Receiver()
r.run()
