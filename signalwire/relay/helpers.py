import logging
from signalwire.blade.messages.execute import Execute
from signalwire.blade.messages.subscription import Subscription

# TODO: move protocols/methods to a constants file

async def setup_protocol(client):
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

async def receive_contexts(client, contexts):
  message = Execute({
    'protocol': client.protocol,
    'method': 'signalwire.receive',
    'params': {
      'contexts': contexts
    }
  })
  response = await client.execute(message)
  logging.info(response['result']['message'])
  return response['result']
