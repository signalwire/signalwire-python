import json
from unittest import TestCase
from signalwire.relay.calling.devices import PhoneDevice, SipDevice, WebRTCDevice, AgoraDevice

class TestDevices(TestCase):

  # PHONE

  def test_phone_with_flattened_params(self):
    device = PhoneDevice({'from': '1234', 'to': '5678'})
    self.assertEqual(device.device_type, 'phone')
    self.assertEqual(device.params, json.loads('{"from_number":"1234","to_number":"5678"}'))
    self.assertEqual(device.serialize(), {'type':'phone', 'params': {'from_number': '1234', 'to_number': '5678'}})

  def test_phone_with_flattened_params_and_timeout(self):
    device = PhoneDevice({'from': '1234', 'to': '5678', 'timeout': 45})
    self.assertEqual(device.device_type, 'phone')
    self.assertEqual(device.params, json.loads('{"from_number":"1234","to_number":"5678","timeout":45}'))
    self.assertEqual(device.serialize(), {'type':'phone', 'params': {'from_number': '1234', 'to_number': '5678', 'timeout': 45}})

  def test_phone_with_nested_params(self):
    options = json.loads('{"type":"phone","params":{"from_number":"1234","to_number":"5678"}}')
    device = PhoneDevice(options)
    self.assertEqual(device.device_type, 'phone')
    self.assertEqual(device.params, json.loads('{"from_number":"1234","to_number":"5678"}'))
    self.assertEqual(device.serialize(), {'type':'phone', 'params': {'from_number': '1234', 'to_number': '5678'}})

  def test_phone_with_nested_params_and_timeout(self):
    options = json.loads('{"type":"phone","params":{"from_number":"1234","to_number":"5678","timeout":30}}')
    device = PhoneDevice(options)
    self.assertEqual(device.device_type, 'phone')
    self.assertEqual(device.params, json.loads('{"from_number":"1234","to_number":"5678","timeout":30}'))
    self.assertEqual(device.serialize(), {'type':'phone', 'params': {'from_number': '1234', 'to_number': '5678', 'timeout': 30}})

  # SIP

  def test_sip_with_flattened_params(self):
    headers = {
      'X-account-id': '1234',
      'X-account-foo': 'baz'
    }
    device = SipDevice({'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'headers': headers})
    self.assertEqual(device.device_type, 'sip')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.sip.com","to":"user@example.sip.com","headers":{"X-account-id":"1234","X-account-foo":"baz"}}'))
    self.assertEqual(device.serialize(), {'type':'sip', 'params': {'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'headers': headers}})

  def test_sip_with_flattened_params_and_timeout(self):
    device = SipDevice({'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'timeout': 45})
    self.assertEqual(device.device_type, 'sip')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.sip.com","to":"user@example.sip.com","timeout":45}'))
    self.assertEqual(device.serialize(), {'type':'sip', 'params': {'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'timeout': 45}})

  def test_sip_with_flattened_params_and_codecs(self):
    device = SipDevice({'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'codecs': ['C1', 'C2']})
    self.assertEqual(device.device_type, 'sip')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.sip.com","to":"user@example.sip.com","codecs":["C1","C2"]}'))
    self.assertEqual(device.serialize(), {'type':'sip', 'params': {'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'codecs': ['C1', 'C2']}})

  def test_sip_with_nested_params(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.sip.com","to":"user@example.sip.com","timeout":30,"headers":{"X-account-id":"1234","X-account-foo":"baz"}}}')
    device = SipDevice(options)
    self.assertEqual(device.device_type, 'sip')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.sip.com","to":"user@example.sip.com","timeout":30,"headers":{"X-account-id":"1234","X-account-foo":"baz"}}'))
    self.assertEqual(device.serialize(), {'type':'sip', 'params': {'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'timeout': 30, 'headers': { 'X-account-id': '1234', 'X-account-foo': 'baz' }}})

  def test_sip_with_nested_params_and_webrtcmedia(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.sip.com","to":"user@example.sip.com","webrtc_media":true,"headers":{"X-account-id":"1234","X-account-foo":"baz"}}}')
    device = SipDevice(options)
    self.assertEqual(device.device_type, 'sip')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.sip.com","to":"user@example.sip.com","webrtc_media":true,"headers":{"X-account-id":"1234","X-account-foo":"baz"}}'))
    self.assertEqual(device.serialize(), {'type':'sip', 'params': {'from': 'user@somewhere.sip.com', 'to': 'user@example.sip.com', 'webrtc_media': True, 'headers': { 'X-account-id': '1234', 'X-account-foo': 'baz' }}})

  # WEBRTC

  def test_webrtc_with_flattened_params(self):
    device = WebRTCDevice({'from': 'user@somewhere.com', 'to': 'room123@example.com', 'timeout': 45})
    self.assertEqual(device.device_type, 'webrtc')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room123@example.com","timeout":45}'))
    self.assertEqual(device.serialize(), {'type':'webrtc', 'params': {'from': 'user@somewhere.com', 'to': 'room123@example.com', 'timeout': 45}})

  def test_webrtc_with_flattened_params_and_codecs(self):
    device = WebRTCDevice({'from': 'user@somewhere.com', 'to': 'room123@example.com', 'codecs': ['C1', 'C2']})
    self.assertEqual(device.device_type, 'webrtc')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room123@example.com","codecs":["C1","C2"]}'))
    self.assertEqual(device.serialize(), {'type':'webrtc', 'params': {'from': 'user@somewhere.com', 'to': 'room123@example.com', 'codecs': ['C1', 'C2']}})

  def test_webrtc_with_nested_params(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.com","to":"room123@example.com","timeout":30}}')
    device = WebRTCDevice(options)
    self.assertEqual(device.device_type, 'webrtc')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room123@example.com","timeout":30}'))
    self.assertEqual(device.serialize(), {'type':'webrtc', 'params': {'from': 'user@somewhere.com', 'to': 'room123@example.com', 'timeout': 30}})

  def test_webrtc_with_nested_params_and_codecs(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.com","to":"room123@example.com","codecs":["C1"]}}')
    device = WebRTCDevice(options)
    self.assertEqual(device.device_type, 'webrtc')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room123@example.com","codecs":["C1"]}'))
    self.assertEqual(device.serialize(), {'type':'webrtc', 'params': {'from': 'user@somewhere.com', 'to': 'room123@example.com', 'codecs': ['C1']}})

  # AGORA

  def test_agora_with_flattened_params(self):
    device = AgoraDevice({'from': 'user@somewhere.com', 'to': 'room-example', 'app_id': 'uuid', 'channel': '1111', 'timeout': 40})
    self.assertEqual(device.device_type, 'agora')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room-example","appid":"uuid","channel":"1111","timeout":40}'))
    self.assertEqual(device.serialize(), {'type':'agora', 'params': {'from': 'user@somewhere.com', 'to': 'room-example', 'appid': 'uuid', 'channel': '1111', 'timeout': 40}})

  def test_agora_with_nested_params(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.com","to":"room-example","appid":"uuid","channel":"1111"}}')
    device = AgoraDevice(options)
    self.assertEqual(device.device_type, 'agora')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room-example","appid":"uuid","channel":"1111"}'))
    self.assertEqual(device.serialize(), {'type':'agora', 'params': {'from': 'user@somewhere.com', 'to': 'room-example', 'appid': 'uuid', 'channel': '1111'}})

  def test_agora_with_nested_params_and_agoramedia(self):
    options = json.loads('{"type":"sip","params":{"from":"user@somewhere.com","to":"room-example","appid":"uuid","channel":"1111"}}')
    device = AgoraDevice(options)
    self.assertEqual(device.device_type, 'agora')
    self.assertEqual(device.params, json.loads('{"from":"user@somewhere.com","to":"room-example","appid":"uuid","channel":"1111"}'))
    self.assertEqual(device.serialize(), {'type':'agora', 'params': {'from': 'user@somewhere.com', 'to': 'room-example', 'appid': 'uuid', 'channel': '1111'}})
