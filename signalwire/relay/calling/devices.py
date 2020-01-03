from abc import ABC, abstractmethod, abstractproperty
import logging
from .constants import DeviceType

class Device():
  @classmethod
  def factory(cls, options):
    dtype = options.get('type', None)
    if dtype == DeviceType.PHONE:
      return PhoneDevice(options)
    elif dtype == DeviceType.SIP:
      return SipDevice(options)
    elif dtype == DeviceType.WEBRTC:
      return WebRTCDevice(options)
    elif dtype == DeviceType.AGORA:
      return AgoraDevice(options)
    else:
      logging.warn(f'Unknow device type: {dtype}')

class BaseDevice(ABC):
  device_type = None

  def __init__(self, options):
    try:
      self.params = options['params']
    except Exception:
      self._build_params(options)

  @abstractproperty
  def from_endpoint(self):
    pass

  @abstractproperty
  def to_endpoint(self):
    pass

  @abstractmethod
  def _build_params(self, options):
    pass

  @property
  def timeout(self):
    return self.params.get('timeout', None)

  def serialize(self, **kwargs):
    return { 'type': self.device_type, 'params': self.params }

  def _add_timeout(self, options):
    if 'timeout' in options:
      self.params['timeout'] = options['timeout']

class PhoneDevice(BaseDevice):
  device_type = DeviceType.PHONE

  @property
  def from_endpoint(self):
    return self.params['from_number']

  @property
  def to_endpoint(self):
    return self.params['to_number']

  def _build_params(self, options):
    self.params = {
      'from_number': options.get('from', None),
      'to_number': options.get('to', None)
    }
    self._add_timeout(options)

class SipDevice(BaseDevice):
  device_type = DeviceType.SIP

  @property
  def from_endpoint(self):
    return self.params['from']

  @property
  def to_endpoint(self):
    return self.params['to']

  def _build_params(self, options):
    self.params = {
      'from': options['from'],
      'to': options['to']
    }
    self._add_timeout(options)
    if 'headers' in options:
      self.params['headers'] = options['headers']
    if 'codecs' in options:
      self.params['codecs'] = options['codecs']
    if 'webrtc_media' in options:
      self.params['webrtc_media'] = options['webrtc_media']

class WebRTCDevice(BaseDevice):
  device_type = DeviceType.WEBRTC

  @property
  def from_endpoint(self):
    return self.params['from']

  @property
  def to_endpoint(self):
    return self.params['to']

  def _build_params(self, options):
    self.params = {
      'from': options.get('from', None),
      'to': options.get('to', None)
    }
    self._add_timeout(options)
    if 'codecs' in options:
      self.params['codecs'] = options['codecs']

class AgoraDevice(BaseDevice):
  device_type = DeviceType.AGORA

  @property
  def from_endpoint(self):
    return self.params['from']

  @property
  def to_endpoint(self):
    return self.params['to']

  def _build_params(self, options):
    self.params = {
      'from': options.get('from', None),
      'to': options.get('to', None),
      'appid': options.get('app_id', None),
      'channel': options.get('channel', None)
    }
    self._add_timeout(options)
