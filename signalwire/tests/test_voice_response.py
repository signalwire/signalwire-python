from unittest import TestCase

class TestVoiceResponse(TestCase):
  def test_returns_laml(self):
    from signalwire.voice_response import VoiceResponse, Dial
    r = VoiceResponse()
    r.say("Welcome to SignalWire!")
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Welcome to SignalWire!</Say></Response>')

  def test_supports_virtual_agent(self):
    from signalwire.voice_response import VoiceResponse
    r = VoiceResponse()
    connect = r.connect(action='http://example.com/action')
    connect.virtual_agent(connectorName='project', statusCallback='https://mycallbackurl.com')
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Connect action="http://example.com/action"><VirtualAgent connectorName="project" statusCallback="https://mycallbackurl.com" /></Connect></Response>')

