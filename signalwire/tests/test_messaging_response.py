from unittest import TestCase

class TestMessagingResponse(TestCase):
  def test_returns_laml(self):
    from signalwire.messaging_response import MessagingResponse
    r = MessagingResponse()
    r.message("This is a message from SignalWire!")
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Message>This is a message from SignalWire!</Message></Response>')

