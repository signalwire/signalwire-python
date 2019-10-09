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

def has_volume_control(cls):
  async def volume(self, volume):
    msg = Execute({
      'protocol': self.call.calling.client.protocol,
      'method': f'{self.method}.volume',
      'params': {
        'node_id': self.call.node_id,
        'call_id': self.call.id,
        'control_id': self.control_id,
        'volume': float(volume)
      }
    })
    try:
      await self.call.calling.client.execute(msg)
      return True
    except Exception:
      return False

  setattr(cls, 'volume', volume)
  return cls
