from twilio.rest import Client as TwilioClient
from twilio.rest.api import Api as TwilioApi
from twilio.base.exceptions import TwilioRestException

import sys
from six import u

def patched_str(self):
    """ Try to pretty-print the exception, if this is going on screen. """

    def red(words):
      return u("\033[31m\033[49m%s\033[0m") % words

    def white(words):
      return u("\033[37m\033[49m%s\033[0m") % words

    def blue(words):
      return u("\033[34m\033[49m%s\033[0m") % words

    def teal(words):
      return u("\033[36m\033[49m%s\033[0m") % words

    def get_uri(code):
       return "https://www.signalwire.com/docs/errors/{0}".format(code)

    # If it makes sense to print a human readable error message, try to
    # do it. The one problem is that someone might catch this error and
    # try to display the message from it to an end user.
    if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
      msg = (
        "\n{red_error} {request_was}\n\n{http_line}"
        "\n\n{sw_returned}\n\n{message}\n".format(
          red_error=red("HTTP Error"),
          request_was=white("Your request was:"),
          http_line=teal("%s %s" % (self.method, self.uri)),
          sw_returned=white(
            "Signalwire returned the following information:"),
            message=blue(str(self.msg))
          ))
      if self.code:
        msg = "".join([msg, "\n{more_info}\n\n{uri}\n\n".format(
          more_info=white("More information may be available here:"),
          uri=blue(get_uri(self.code))),
        ])
      return msg
    else:
      return "HTTP {0} error: {1}".format(self.status, self.msg)

class Client(TwilioClient):
  def __init__(self, *args, **kwargs):
    signalwire_base_url = kwargs.pop('signalwire_base_url', "https://api.signalwire.com")
    super(Client, self).__init__(*args, **kwargs)
    self._api = TwilioApi(self)
    self._api.base_url = signalwire_base_url
    TwilioRestException.__str__ = patched_str


