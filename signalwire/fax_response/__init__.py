from twilio.twiml.fax_response import FaxResponse as TwilioFaxResponse
from twilio.twiml import TwiML

class FaxResponse(TwilioFaxResponse):
  def reject(self, **kwargs):
    """
    Create a <Reject> element
    :param kwargs: additional attributes
    :returns: <Reject> element
    """
    return self.nest(Reject(**kwargs))

class Reject(TwiML):
  """ <Reject> TwiML Verb """

  def __init__(self, **kwargs):
    super(Reject, self).__init__(**kwargs)
    self.name = 'Reject'
