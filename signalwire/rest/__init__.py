from twilio.rest import Client as TwilioClient
from twilio.rest.api import Api as TwilioApi

class Client(TwilioClient):
  def __init__(self, *args, **kwargs):
    signalwire_base_url = kwargs.pop('signalwire_base_url', "https://api.twilio.com")
    super(Client, self).__init__(*args, **kwargs)
    self._api = TwilioApi(self)
    self._api.base_url = signalwire_base_url
