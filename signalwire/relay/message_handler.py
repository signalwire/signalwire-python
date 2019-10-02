import logging

def handle_inbound_message(client, message):
  if message.method == 'blade.netcast':
    pass
  elif message.method == 'blade.broadcast':
    _blade_broadcast(client, message.params)

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
    logging.info('Handle messaging notification')
