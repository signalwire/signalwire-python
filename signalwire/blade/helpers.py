import asyncio

def safe_invoke_callback(callback, *args, **kwargs):
  if asyncio.iscoroutinefunction(callback):
    asyncio.create_task(callback(*args, **kwargs))
  else:
    callback(*args, **kwargs)
