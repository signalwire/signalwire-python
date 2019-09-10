from signalwire.blade.messages.message import Message

class Execute(Message):

  def __init__(self, params):
    self.method = 'blade.execute'
    super().__init__(params=params)
