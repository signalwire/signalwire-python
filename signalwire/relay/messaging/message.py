class Message:
  def __init__(self, params={}):
    self.id = params.get('message_id', None)
    self.state = params.get('message_state', None)
    self.context = params.get('context', None)
    self.from_number = params.get('from_number', None)
    self.to_number = params.get('to_number', None)
    self.body = params.get('body', None)
    self.direction = params.get('direction', None)
    self.media = params.get('media', None)
    self.segments = params.get('segments', None)
    self.tags = params.get('tags', None)
    self.reason = params.get('reason', None)
