from twilio.rest import Client as TwilioClient
from twilio.rest.api import Api as TwilioApi

class Client(TwilioClient):
  def __init__(self, *args, **kwargs):
    super(Client, self).__init__(args, kwargs)
    self._api = TwilioApi(self)
    print(kwargs.get('signalwire_base_url', "https://api.twilio.com"))
    self._api.base_url = kwargs.get('signalwire_base_url', "https://api.twilio.com")
