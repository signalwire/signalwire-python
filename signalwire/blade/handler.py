from .helpers import safe_invoke_callback

GLOBAL = 'GLOBAL'
_queue = {}

def register(*, event, callback, suffix=GLOBAL):
  global _queue

  event = build_event_name(event, suffix)
  if event not in _queue:
    _queue[event] = []
  _queue[event].append(callback)

def register_once(*, event, callback, suffix=GLOBAL):
  global _queue

  def cb(*args):
    unregister(event=event, callback=cb, suffix=suffix)
    callback(*args)

  register(event=event, callback=cb, suffix=suffix)

def unregister(*, event, callback=None, suffix=GLOBAL):
  global _queue

  if is_queued(event, suffix) is False:
    return False
  event = build_event_name(event, suffix)
  if callback is None:
    _queue[event] = []
  else:
    for index, handler in enumerate(_queue[event]):
      if callback == handler:
        del _queue[event][index]

  if (_queue[event]) == 0:
    del _queue[event]

  return True

def unregister_all(event):
  global _queue

  target = build_event_name(event, '')
  for event in list(_queue.keys()):
    if event.find(target) == 0:
      del _queue[event]

def trigger(event, *args, suffix=GLOBAL, **kwargs):
  global _queue

  if is_queued(event, suffix) is False:
    return False
  event = build_event_name(event, suffix)
  for callback in _queue[event]:
    safe_invoke_callback(callback, *args, **kwargs)
  return True

def is_queued(event, suffix=GLOBAL):
  global _queue

  event = build_event_name(event, suffix)
  return event in _queue and len(_queue[event]) > 0

def queue_size(event, suffix=GLOBAL):
  global _queue

  if is_queued(event, suffix) is False:
    return 0
  event = build_event_name(event, suffix)
  return len(_queue[event])

def clear():
  global _queue

  _queue = {}

def build_event_name(event, suffix):
  return "{0}|{1}".format(event.strip(), suffix.strip())
