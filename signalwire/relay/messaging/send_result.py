class SendResult:
  def __init__(self, result={}):
    self.successful = result.get('code', None) == '200'
    self.message_id = result.get('message_id', None)
