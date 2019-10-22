class Method:
  BEGIN = 'calling.begin'
  ANSWER = 'calling.answer'
  END = 'calling.end'
  CONNECT = 'calling.connect'
  PLAY = 'calling.play'
  RECORD = 'calling.record'
  RECEIVE_FAX = 'calling.receive_fax'
  SEND_FAX = 'calling.send_fax'
  SEND_DIGITS = 'calling.send_digits'
  TAP = 'calling.tap'

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
  SEND_DIGITS = 'calling.call.send_digits'

class CallState:
  ALL = ['created', 'ringing', 'answered', 'ending', 'ended']
  NONE = 'none'
  CREATED = 'created'
  RINGING = 'ringing'
  ANSWERED = 'answered'
  ENDING = 'ending'
  ENDED = 'ended'

class ConnectState:
  DISCONNECTED = 'disconnected'
  CONNECTING = 'connecting'
  CONNECTED = 'connected'
  FAILED = 'failed'

class DisconnectReason:
  ERROR = 'error'
  BUSY = 'busy'

class CallPlayState:
  PLAYING = 'playing'
  ERROR = 'error'
  FINISHED = 'finished'

class MediaType:
  AUDIO = 'audio'
  TTS = 'tts'
  SILENCE = 'silence'

class CallRecordState:
  RECORDING = 'recording'
  NOINPUT = 'no_input'
  FINISHED = 'finished'

class RecordType:
  AUDIO = 'audio'

class CallFaxState:
  PAGE = 'page'
  ERROR = 'error'
  FINISHED = 'finished'

class CallSendDigitsState:
  FINISHED = 'finished'

class CallTapState:
  TAPPING = 'tapping'
  FINISHED = 'finished'

class TapType:
  AUDIO = 'audio'
