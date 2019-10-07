def reduce_connect_params(devices, default_from, default_timeout=None, nested=False):
  final = []
  for device in devices:
    if isinstance(device, list):
      final.append(reduce_connect_params(device, default_from, default_timeout, True))
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
