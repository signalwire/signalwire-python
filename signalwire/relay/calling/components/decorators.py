from signalwire.blade.messages.execute import Execute

async def _execute(self, method):
  msg = Execute({
    'protocol': self.call.calling.client.protocol,
    'method': method,
    'params': {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id
    }
  })
  try:
    await self.call.calling.client.execute(msg)
    return True
  except Exception:
    # logging.error('Relay command failed: {0}'.format(str(error)))
    return False

def stoppable(cls):
  async def stop(self):
    return await _execute(self, f'{self.method}.stop')
  setattr(cls, 'stop', stop)
  return cls

def pausable(cls):
  async def pause(self):
    return await _execute(self, f'{self.method}.pause')
  setattr(cls, 'pause', pause)
  return cls

def resumable(cls):
  async def resume(self):
    return await _execute(self, f'{self.method}.resume')
  setattr(cls, 'resume', resume)
  return cls
