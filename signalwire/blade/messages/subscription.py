from signalwire.blade.messages.message import Message

class Subscription(Message):

  def __init__(self, params):
    self.method = 'blade.subscription'
    super().__init__(params=params)
