from signalwire.blade.messages.execute import Execute
from signalwire.blade.messages.subscription import Subscription

async def setup_protocol(client):
  # move proto/method to a constants file
  setup_message = Execute({
    'protocol': 'signalwire',
    'method': 'setup',
    'params': {}
  })
  response = await client.execute(setup_message)
  protocol = response['result']['protocol']
  subscribe_message = Subscription({
    'command': 'add',
    'protocol': protocol,
    'channels': ['notifications']
  })
  response = await client.execute(subscribe_message)
  return protocol
