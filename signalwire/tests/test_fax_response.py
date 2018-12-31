from unittest import TestCase

class TestFaxResponse(TestCase):
  def test_returns_laml(self):
    from signalwire.fax_response import FaxResponse
    r = FaxResponse()
    r.receive(action = '/foo/bar')
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Receive action="/foo/bar" /></Response>')

  def test_reject_laml(self):
    from signalwire.fax_response import FaxResponse
    r = FaxResponse()
    obj = r.reject()
    self.assertEqual(str(r), '<?xml version="1.0" encoding="UTF-8"?><Response><Reject /></Response>')


