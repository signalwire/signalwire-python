import json
from uuid import uuid4

class Message:
  def __init__(self, **kwargs):
    self.jsonrpc = '2.0'
    self.id = kwargs.pop('id', str(uuid4()))
    if 'method' in kwargs:
      self.method = kwargs.pop('method')
    if 'params' in kwargs:
      self.params = kwargs.pop('params')
    if 'error' in kwargs:
      self.error = kwargs.pop('error')
    if 'result' in kwargs:
      self.result = kwargs.pop('result')

  def to_json(self, **kwargs):
    return json.dumps(self.__dict__, separators=(',', ':'), **kwargs)

  @classmethod
  def from_json(cls, json_str):
    json_dict = json.loads(json_str)
    return cls(**json_dict)
