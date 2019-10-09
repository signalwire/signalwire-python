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
    return False

def stoppable(cls):
  def stop(self):
    return _execute(self, f'{self.method}.stop')
  setattr(cls, 'stop', stop)
  return cls

def pausable(cls):
  def pause(self):
    return _execute(self, f'{self.method}.pause')
  setattr(cls, 'pause', pause)
  return cls

def resumable(cls):
  def resume(self):
    return _execute(self, f'{self.method}.resume')
  setattr(cls, 'resume', resume)
  return cls
