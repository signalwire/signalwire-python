def prepare_connect_devices(devices, default_from, default_timeout=None, nested=False):
  final = []
  for device in devices:
    if isinstance(device, list):
      final.append(prepare_connect_devices(device, default_from, default_timeout, True))
    elif isinstance(device, dict):
      params = {
        'from_number': device.get('from_number', default_from),
        'to_number': device.get('to_number', '')
      }
      timeout = device.get('timeout', default_timeout)
      if timeout:
        params['timeout'] = int(timeout)
      tmp = {
        'type': device.get('call_type', 'phone'),
        'params': params
      }
      final.append(tmp if nested else [tmp])
  return final

def prepare_media_list(media_list):
  final = []
  for media in media_list:
    if not isinstance(media, dict):
      continue
    media_type = media.pop('type', '')
    final.append({
      'type': media_type,
      'params': media
    })
  return final
