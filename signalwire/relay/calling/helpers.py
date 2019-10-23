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

def prepare_collect_params(prompt_type, params):
  collect = {}
  if prompt_type == 'both':
    collect['speech'] = {}
    collect['digits'] = {}
  elif prompt_type == 'digits':
    collect['digits'] = {}
  elif prompt_type == 'speech':
    collect['speech'] = {}

  # TODO: support partial_results
  if 'initial_timeout' in params:
    collect['initial_timeout'] = params['initial_timeout']
  if 'digits_max' in params:
    collect['digits']['max'] = params['digits_max']
  if 'digits_terminators' in params:
    collect['digits']['terminators'] = params['digits_terminators']
  if 'digits_timeout' in params:
    collect['digits']['digit_timeout'] = params['digits_timeout']
  if 'end_silence_timeout' in params:
    collect['speech']['end_silence_timeout'] = params['end_silence_timeout']
  if 'speech_timeout' in params:
    collect['speech']['speech_timeout'] = params['speech_timeout']
  if 'speech_language' in params:
    collect['speech']['language'] = params['speech_language']
  if 'speech_hints' in params:
    collect['speech']['hints'] = params['speech_hints']

  return collect

def prepare_prompt_media_list(params, kwargs):
  # helper method to build media_list for prompt_ringtone and prompt_tts
  for k in ['duration', 'language', 'gender']:
    if k in kwargs:
      params[k] = kwargs[k]
  return params
