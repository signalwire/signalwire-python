from twilio.rest import Client as TwilioClient
from twilio.rest.api import Api as TwilioApi
from twilio.base.exceptions import TwilioRestException
from urllib.parse import urlparse, ParseResult
from twilio.rest.api.v2010.account.application import ApplicationInstance
from twilio.rest.api.v2010.account.call import CallInstance
from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest.api.v2010.account.available_phone_number.local import LocalInstance
from twilio.rest.api.v2010.account.available_phone_number.toll_free import TollFreeInstance
from twilio.rest.api.v2010.account.incoming_phone_number import IncomingPhoneNumberInstance
from twilio.base import deserialize

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

def patched_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the CallInstance

    :returns: twilio.rest.api.v2010.account.call.CallInstance
    :rtype: twilio.rest.api.v2010.account.call.CallInstance
    """
    super(CallInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'account_sid': payload['account_sid'],
        'annotation': payload.get('annotation', ''),
        'answered_by': payload['answered_by'],
        'api_version': payload['api_version'],
        'caller_name': payload['caller_name'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'direction': payload['direction'],
        'duration': payload['duration'],
        'end_time': deserialize.rfc2822_datetime(payload['end_time']),
        'forwarded_from': payload['forwarded_from'],
        'from_': payload['from'],
        'from_formatted': payload.get('from_formatted', ''),
        'group_sid': payload.get('group_sid', ''),
        'parent_call_sid': payload['parent_call_sid'],
        'phone_number_sid': payload['phone_number_sid'],
        'price': deserialize.decimal(payload['price']),
        'price_unit': payload.get('price_unit', ''),
        'sid': payload['sid'],
        'start_time': deserialize.rfc2822_datetime(payload['start_time']),
        'status': payload['status'],
        'subresource_uris': payload['subresource_uris'],
        'to': payload['to'],
        'to_formatted': payload.get('to_formatted', ''),
        'uri': payload['uri'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }


def patched_applicationinstance_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the ApplicationInstance

    :returns: twilio.rest.api.v2010.account.application.ApplicationInstance
    :rtype: twilio.rest.api.v2010.account.application.ApplicationInstance
    """
    super(ApplicationInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'account_sid': payload['account_sid'],
        'api_version': payload['api_version'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'friendly_name': payload['friendly_name'],
        'sid': payload['sid'],
        'sms_fallback_method': payload['sms_fallback_method'],
        'sms_fallback_url': payload['sms_fallback_url'],
        'sms_method': payload['sms_method'],
        'sms_status_callback': payload['sms_status_callback'],
        'sms_url': payload['sms_url'],
        'status_callback': payload['status_callback'],
        'status_callback_method': payload['status_callback_method'],
        'uri': payload['uri'],
        'voice_caller_id_lookup': payload['voice_caller_id_lookup'],
        'voice_fallback_method': payload['voice_fallback_method'],
        'voice_fallback_url': payload['voice_fallback_url'],
        'voice_method': payload['voice_method'],
        'voice_url': payload['voice_url'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

def patched_localinstance_init(self, version, payload, account_sid, country_code):
    """
    Initialize the LocalInstance
    :returns: twilio.rest.api.v2010.account.available_phone_number.local.LocalInstance
    :rtype: twilio.rest.api.v2010.account.available_phone_number.local.LocalInstance
    """
    super(LocalInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'friendly_name': payload['friendly_name'],
        'phone_number': payload['phone_number'],
        'lata': payload['lata'],
        'rate_center': payload['rate_center'],
        'latitude': deserialize.decimal(payload['latitude']),
        'longitude': deserialize.decimal(payload['longitude']),
        'region': payload['region'],
        'postal_code': payload['postal_code'],
        'iso_country': payload['iso_country'],
        'beta': payload['beta'],
        'capabilities': payload['capabilities'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'country_code': country_code, }

def patched_incommingphonenumberinstance_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the IncomingPhoneNumberInstance

    :returns: twilio.rest.api.v2010.account.incoming_phone_number.IncomingPhoneNumberInstance
    :rtype: twilio.rest.api.v2010.account.incoming_phone_number.IncomingPhoneNumberInstance
    """
    super(IncomingPhoneNumberInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'api_version': payload['api_version'],
        'beta': payload['beta'],
        'capabilities': payload['capabilities'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'friendly_name': payload['friendly_name'],
        'phone_number': payload['phone_number'],
        'sid': payload['sid'],
        'sms_application_sid': payload['sms_application_sid'],
        'sms_fallback_method': payload['sms_fallback_method'],
        'sms_fallback_url': payload['sms_fallback_url'],
        'sms_method': payload['sms_method'],
        'sms_url': payload['sms_url'],
        'status_callback': payload['status_callback'],
        'status_callback_method': payload['status_callback_method'],
        'uri': payload['uri'],
        'voice_application_sid': payload['voice_application_sid'],
        'voice_caller_id_lookup': payload['voice_caller_id_lookup'],
        'voice_fallback_method': payload['voice_fallback_method'],
        'voice_fallback_url': payload['voice_fallback_url'],
        'voice_method': payload['voice_method'],
        'voice_url': payload['voice_url'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

def patched_tollfreeinstance_init(self, version, payload, account_sid, country_code):
    """
    Initialize the TollFreeInstance

    :returns: twilio.rest.api.v2010.account.available_phone_number.toll_free.TollFreeInstance
    :rtype: twilio.rest.api.v2010.account.available_phone_number.toll_free.TollFreeInstance
    """
    super(TollFreeInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'friendly_name': payload['friendly_name'],
        'phone_number': payload['phone_number'],
        'lata': payload['lata'],
        'rate_center': payload['rate_center'],
        'latitude': deserialize.decimal(payload['latitude']),
        'longitude': deserialize.decimal(payload['longitude']),
        'region': payload['region'],
        'postal_code': payload['postal_code'],
        'iso_country': payload['iso_country'],
        'beta': payload['beta'],
        'capabilities': payload['capabilities'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'country_code': country_code, }

def patched_message_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the MessageInstance
    :returns: twilio.rest.api.v2010.account.message.MessageInstance
    :rtype: twilio.rest.api.v2010.account.message.MessageInstance
    """
    super(MessageInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'account_sid': payload['account_sid'],
        'api_version': payload['api_version'],
        'body': payload['body'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'date_sent': deserialize.rfc2822_datetime(payload['date_sent']),
        'direction': payload['direction'],
        'error_code': deserialize.integer(payload['error_code']),
        'error_message': payload['error_message'],
        'from_': payload['from'],
        'messaging_service_sid': payload.get('messaging_service_sid', ''),
        'num_media': payload['num_media'],
        'num_segments': payload['num_segments'],
        'price': deserialize.decimal(payload['price']),
        'price_unit': payload['price_unit'],
        'sid': payload['sid'],
        'status': payload['status'],
        'subresource_uris': payload['subresource_uris'],
        'to': payload['to'],
        'uri': payload['uri'],
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

class Client(TwilioClient):
  def __init__(self, *args, **kwargs):
    signalwire_space_url = kwargs.pop('signalwire_space_url', "api.signalwire.com")

    p = urlparse(signalwire_space_url, 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    p = ParseResult('https', netloc, path, *p[3:])

    super(Client, self).__init__(*args, **kwargs)
    self._api = TwilioApi(self)
    self._api.base_url = p.geturl()
    TwilioRestException.__str__ = patched_str
    CallInstance.__init__ = patched_init
    MessageInstance.__init__ = patched_message_init
    LocalInstance.__init__ = patched_localinstance_init
    TollFreeInstance.__init__ = patched_tollfreeinstance_init
    ApplicationInstance.__init__ = patched_applicationinstance_init
    IncomingPhoneNumberInstance.__init__ = patched_incommingphonenumberinstance_init
