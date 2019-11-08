from signalwire.blade.messages.message import Message

class Ping(Message):

  def __init__(self, timestamp=None):
    self.method = 'blade.ping'
    params = { 'timestamp': timestamp } if timestamp else {}
    super().__init__(params=params)
