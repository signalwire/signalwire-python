import json

def default(obj):
  try:
    return obj.serialize()
  except:
    pass
  # Let Python raise the TypeError
  return json.dumps(obj)

class JSONRPCEncoder():
  @classmethod
  def encode(cls, dictionary={}, **kwargs):
    return json.dumps(dictionary, default=default, separators=(',', ':'), **kwargs)
