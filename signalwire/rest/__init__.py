class Client:
  def __init__(self, *args, **kwargs):
    self._api = None
    self.monkey_base_url = kwargs.get('signalwire_base_url', "https://api.twilio.com")

    from twilio.rest import Client as twilio_client
    twilio_client.api = self.__MonkeyApi
    self._client = twilio_client(args, kwargs)

  @property
  def create(self):
    return self._client

  @property
  def __MonkeyApi(self):
    """
    Access the Api Twilio Domain
    :returns: Api Twilio Domain
    :rtype: twilio.rest.api.Api
    """
    if self._api is None:
      from twilio.rest.api import Api
      self._api = Api(self)
      self._api.base_url = self.monkey_base_url
    return self._api

