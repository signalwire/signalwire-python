from unittest import TestCase

class TestVoiceResponse(TestCase):
  def test_returns_laml(self):
    from signalwire.voice_response import VoiceResponse
    r = VoiceResponse()
    r.say("Welcome to SignalWire!")
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Welcome to SignalWire!</Say></Response>')

