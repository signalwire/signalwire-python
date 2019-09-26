class Method:
  BEGIN = 'calling.begin'
  ANSWER = 'calling.answer'
  END = 'calling.end'

class Notification:
  STATE = 'calling.call.state'
  CONNECT = 'calling.call.connect'
  RECORD = 'calling.call.record'
  PLAY = 'calling.call.play'
  COLLECT = 'calling.call.collect'
  RECEIVE = 'calling.call.receive'
  FAX = 'calling.call.fax'
  DETECT = 'calling.call.detect'
  TAP = 'calling.call.tap'
  SENDDIGITS = 'calling.call.send_digits'

class CallState:
  NONE = 'none'
  CREATED = 'created'
  RINGING = 'ringing'
  ANSWERED = 'answered'
  ENDING = 'ending'
  ENDED = 'ended'

class DisconnectReason:
  ERROR = 'error'
  BUSY = 'busy'
