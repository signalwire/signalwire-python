import logging
from .constants import BladeMethod

def handle_inbound_message(client, message):
  if message.method == BladeMethod.NETCAST:
    pass
  elif message.method == BladeMethod.BROADCAST:
    _blade_broadcast(client, message.params)
  elif message.method == BladeMethod.DISCONNECT:
    client._idle = True

def _blade_broadcast(client, params):
  if client.protocol != params['protocol']:
    logging.warn('Client protocol mismatch.')
    return

  if params['event'] == 'queuing.relay.events':
    # FIXME: at the moment all these events are for calling. In the future we'll change the case
    client.calling.notification_handler(params['params'])
  elif params['event'] == 'queuing.relay.tasks':
    client.tasking.notification_handler(params['params'])
  elif params['event'] == 'queuing.relay.messaging':
    client.messaging.notification_handler(params['params'])
