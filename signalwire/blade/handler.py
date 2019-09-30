from .helpers import safe_invoke_callback

GLOBAL = 'GLOBAL'
_queue = {}

def register(event, callback, unique_id = GLOBAL):
  global _queue

  event = build_event_name(event, unique_id)
  if event not in _queue:
    _queue[event] = []
  _queue[event].append(callback)

def register_once(event, callback, unique_id = GLOBAL):
  global _queue

  def cb(*args):
    unregister(event, cb, unique_id)
    callback(*args)

  register(event, cb, unique_id)

def unregister(event, callback = None, unique_id = GLOBAL):
  global _queue

  if is_queued(event, unique_id) is False:
    return False
  event = build_event_name(event, unique_id)
  if callback is None:
    _queue[event] = []
  else:
    for index, handler in enumerate(_queue[event]):
      if callback == handler:
        del _queue[event][index]

  if (_queue[event]) == 0:
    del _queue[event]

  return True

def trigger(event, data, unique_id = GLOBAL):
  global _queue

  if is_queued(event, unique_id) is False:
    return False
  event = build_event_name(event, unique_id)
  for callback in _queue[event]:
    safe_invoke_callback(callback, data)
  return True

def is_queued(event, unique_id = GLOBAL):
  global _queue

  event = build_event_name(event, unique_id)
  return event in _queue and len(_queue[event]) > 0

def queue_size(event, unique_id = GLOBAL):
  global _queue

  if is_queued(event, unique_id) is False:
    return 0
  event = build_event_name(event, unique_id)
  return len(_queue[event])

def clear():
  global _queue

  _queue = {}

def build_event_name(event, unique_id):
  return "{0}|{1}".format(event.strip(), unique_id.strip())
