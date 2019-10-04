class Method:
  SEND = 'messaging.send'

class Notification:
  STATE = 'messaging.state'
  RECEIVE = 'messaging.receive'

class MessageState:
  QUEUED = 'queued'
  INITIATED = 'initiated'
  SENT = 'sent'
  DELIVERED = 'delivered'
  UNDELIVERED = 'undelivered'
  FAILED = 'failed'

class DisconnectReason:
  ERROR = 'error'
  BUSY = 'busy'
