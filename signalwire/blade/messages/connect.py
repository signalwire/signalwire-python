from signalwire.blade.messages.message import Message

class Connect(Message):

  MAJOR = 2
  MINOR = 3
  REVISION = 0

  def __init__(self, project, token):
    self.method = 'blade.connect'
    params = {
      'version': {
        'major': self.MAJOR,
        'minor': self.MINOR,
        'revision': self.REVISION
      },
      'authentication': {
        'project': project,
        'token': token
      }
    }
    super().__init__(params=params)
