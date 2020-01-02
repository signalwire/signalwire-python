from abc import ABC, abstractmethod, abstractproperty
import logging
from .constants import DeviceType

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

  def serialize(self, **kwargs):
    return { 'type': self.device_type, 'params': self.params }

  def _add_timeout(self, options):
    if 'timeout' in options:
      self.params['timeout'] = options['timeout']


class PhoneDevice(BaseDevice):
  device_type = DeviceType.PHONE

  def from_endpoint(self):
    return self.params['from_number']

  def to_endpoint(self):
    return self.params['to_number']

  def _build_params(self, options):
    self.params = {
      'from_number': options['from'],
      'to_number': options['to']
    }
    self._add_timeout(options)

class SipDevice(BaseDevice):
  device_type = DeviceType.SIP

  def from_endpoint(self):
    return self.params['from']

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

  def from_endpoint(self):
    return self.params['from']

  def to_endpoint(self):
    return self.params['to']

  def _build_params(self, options):
    self.params = {
      'from': options['from'],
      'to': options['to']
    }
    self._add_timeout(options)
    if 'codecs' in options:
      self.params['codecs'] = options['codecs']

class AgoraDevice(BaseDevice):
  device_type = DeviceType.AGORA

  def from_endpoint(self):
    return self.params['from']

  def to_endpoint(self):
    return self.params['to']

  def _build_params(self, options):
    self.params = {
      'from': options['from'],
      'to': options['to'],
      'appid': options['app_id'],
      'channel': options['channel']
    }
    self._add_timeout(options)
