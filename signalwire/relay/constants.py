class Constants:
  HOST = 'relay.signalwire.com'
  READY = 'ready'

class WebSocketEvents:
  OPEN = 'signalwire.socket.open'
  CLOSE = 'signalwire.socket.close'
  MESSAGE = 'signalwire.socket.message'
  ERROR = 'signalwire.socket.error'

class BladeMethod:
  NETCAST = 'blade.netcast'
  BROADCAST = 'blade.broadcast'
  DISCONNECT = 'blade.disconnect'
