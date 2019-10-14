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

def prepare_record_params(record_type, beep, record_format, stereo, direction, initial_timeout, end_silence_timeout, terminators):
  params = {}
  if isinstance(beep, bool):
    params['beep'] = beep
  if record_format is not None:
    params['format'] = record_format
  if isinstance(stereo, bool):
    params['stereo'] = stereo
  if direction is not None:
    params['direction'] = direction
  if initial_timeout is not None:
    params['initial_timeout'] = initial_timeout
  if end_silence_timeout is not None:
    params['end_silence_timeout'] = end_silence_timeout
  if terminators is not None:
    params['terminators'] = terminators
  return { record_type: params }
