try:
  from urllib.parse import urlparse, ParseResult
except ImportError:
  from urlparse import urlparse, ParseResult
from twilio.rest import Client as TwilioClient
from twilio.rest.api import Api as TwilioApi
from twilio.base.exceptions import TwilioRestException
from twilio.base import deserialize

from twilio.rest.api.v2010.account.application import ApplicationInstance
from twilio.rest.api.v2010.account import AccountInstance
from twilio.rest.api.v2010.account.call import CallInstance
from twilio.rest.api.v2010.account.recording import RecordingInstance
from twilio.rest.api.v2010.account.transcription import TranscriptionInstance
from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest.api.v2010.account.available_phone_number.local import LocalInstance
from twilio.rest.api.v2010.account.available_phone_number.toll_free import TollFreeInstance
from twilio.rest.api.v2010.account.incoming_phone_number import IncomingPhoneNumberInstance

from twilio.rest.fax import Fax as TwilioFax
from twilio.rest.fax.v1 import V1 as TwilioV1

import sys
from six import u
import os

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
        'message_status_callback': payload.get('message_status_callback', ''), #missing
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

def patched_accountinstance_init(self, version, payload, sid=None):
        """
        Initialize the AccountInstance
        :returns: twilio.rest.api.v2010.account.AccountInstance
        :rtype: twilio.rest.api.v2010.account.AccountInstance
        """
        super(AccountInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'auth_token': payload['auth_token'],
            'date_created': deserialize.rfc2822_datetime(payload['date_created']),
            'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
            'friendly_name': payload['friendly_name'],
            'owner_account_sid': payload.get('owner_account_sid', ''),
            'sid': payload['sid'],
            'status': payload['status'],
            'subresource_uris': payload['subresource_uris'],
            'type': payload['type'],
            'uri': payload['uri'],
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }


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
        'locality': payload.get('locality', ''), #missing
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

def patched_incomingphonenumberinstance_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the IncomingPhoneNumberInstance

    :returns: twilio.rest.api.v2010.account.incoming_phone_number.IncomingPhoneNumberInstance
    :rtype: twilio.rest.api.v2010.account.incoming_phone_number.IncomingPhoneNumberInstance
    """
    super(IncomingPhoneNumberInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'account_sid': payload.get('account_sid', ''), #missing
        'address_sid': payload.get('address_sid', ''), #missing
        'address_requirements': payload.get('address_requirements', ''), #missing
        'api_version': payload['api_version'],
        'beta': payload['beta'],
        'capabilities': payload['capabilities'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'friendly_name': payload['friendly_name'],
        'identity_sid': payload.get('identity_sid', ''), #missing,
        'phone_number': payload['phone_number'],
        'origin': payload.get('origin', ''), #missing,
        'sid': payload['sid'],
        'sms_application_sid': payload['sms_application_sid'],
        'sms_fallback_method': payload['sms_fallback_method'],
        'sms_fallback_url': payload['sms_fallback_url'],
        'sms_method': payload['sms_method'],
        'sms_url': payload['sms_url'],
        'status_callback': payload['status_callback'],
        'status_callback_method': payload['status_callback_method'],
        'trunk_sid': payload.get('trunk_sid', ''), #missing,
        'uri': payload['uri'],
        'voice_application_sid': payload['voice_application_sid'],
        'voice_caller_id_lookup': payload['voice_caller_id_lookup'],
        'voice_fallback_method': payload['voice_fallback_method'],
        'voice_fallback_url': payload['voice_fallback_url'],
        'voice_method': payload['voice_method'],
        'voice_url': payload['voice_url'],
        'emergency_status': payload.get('emergency_status', ''), #missing,
        'emergency_address_sid': payload.get('emergency_address_sid', ''), #missing,
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
        'locality': payload.get('locality', ''), #missing
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

def patched_recordinginstance_init(self, version, payload, account_sid, sid=None):
    """
    Initialize the RecordingInstance
    :returns: twilio.rest.api.v2010.account.call.recording.RecordingInstance
    :rtype: twilio.rest.api.v2010.account.call.recording.RecordingInstance
    """
    super(RecordingInstance, self).__init__(version)

    # Marshaled Properties
    self._properties = {
        'account_sid': payload['account_sid'],
        'api_version': payload['api_version'],
        'call_sid': payload['call_sid'],
        'conference_sid': payload['conference_sid'],
        'date_created': deserialize.rfc2822_datetime(payload['date_created']),
        'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
        'start_time': deserialize.rfc2822_datetime(payload['start_time']),
        'duration': payload['duration'],
        'sid': payload['sid'],
        'price': deserialize.decimal(payload['price']),
        'uri': payload['uri'],
        'encryption_details': payload.get('encryption_details', ''), #missing
        # 'encryption_details': payload['encryption_details'],
        'price_unit': payload['price_unit'],
        'status': payload['status'],
        'channels': deserialize.integer(payload.get('channels', 1)), #missing
        # 'channels': deserialize.integer(payload['channels']),
        'source': payload['source'],
        'error_code': deserialize.integer(payload['error_code']),
    }

    # Context
    self._context = None
    self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

def patched_transcriptioninstance_init(self, version, payload, account_sid, sid=None):
      """
      Initialize the TranscriptionInstance
      :returns: twilio.rest.api.v2010.account.transcription.TranscriptionInstance
      :rtype: twilio.rest.api.v2010.account.transcription.TranscriptionInstance
      """
      super(TranscriptionInstance, self).__init__(version)

      # Marshaled Properties
      self._properties = {
          'account_sid': payload['account_sid'],
          'api_version': payload['api_version'],
          'date_created': deserialize.rfc2822_datetime(payload['date_created']),
          'date_updated': deserialize.rfc2822_datetime(payload['date_updated']),
          'duration': payload['duration'],
          'price': deserialize.decimal(payload['price']),
          'price_unit': payload['price_unit'],
          'recording_sid': payload['recording_sid'],
          'sid': payload['sid'],
          'status': payload['status'],
          'transcription_text': payload['transcription_text'],
          'type': payload.get('type', ''), #missing parameter
          'uri': payload['uri'],
      }

      # Context
      self._context = None
      self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

def patched_fax_init(self, twilio):
  """
  Initialize the Fax Domain
  :returns: Domain for Fax
  :rtype: twilio.rest.fax.Fax
  """
  super(TwilioFax, self).__init__(twilio)

  self.base_url = ''
  self.account_sid = twilio.account_sid

  # Versions
  self._v1 = None

def patched_fax_v1_init(self, domain):
  """
  Initialize the V1 version of Fax
  :returns: V1 version of Fax
  :rtype: twilio.rest.fax.v1.V1.V1
  """
  super(TwilioV1, self).__init__(domain)
  self.version = "2010-04-01/Accounts/" + domain.account_sid
  self._faxes = None


class Client(TwilioClient):
  def __init__(self, *args, **kwargs):
    if 'signalwire_space_url' in kwargs:
      signalwire_space_url = kwargs.pop('signalwire_space_url', "api.signalwire.com")
    else:
      signalwire_space_url = os.environ['SIGNALWIRE_SPACE_URL']

    p = urlparse(signalwire_space_url, 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    p = ParseResult('https', netloc, path, *p[3:])

    super(Client, self).__init__(*args, **kwargs)
    self._api = TwilioApi(self)
    self._api.base_url = p.geturl()

    TwilioFax.__init__ = patched_fax_init
    TwilioV1.__init__ = patched_fax_v1_init

    self._fax = TwilioFax(self)
    self._fax.base_url = p.geturl()

    TwilioRestException.__str__ = patched_str
    AccountInstance.__init__ = patched_accountinstance_init
    LocalInstance.__init__ = patched_localinstance_init
    TollFreeInstance.__init__ = patched_tollfreeinstance_init
    ApplicationInstance.__init__ = patched_applicationinstance_init
    IncomingPhoneNumberInstance.__init__ = patched_incomingphonenumberinstance_init
    RecordingInstance.__init__ = patched_recordinginstance_init
    TranscriptionInstance.__init__ = patched_transcriptioninstance_init
