import json
from base64 import b64encode
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .constants import Constants

class Task:
  def __init__(self, project, token, host=Constants.HOST):
    self.project = project
    self.token = token
    self.host = host

  def _authorization(self):
    data = f'{self.project}:{self.token}'.encode('utf-8')
    return 'Basic ' + str(b64encode(data), 'utf-8')

  def deliver(self, context, message):
    uri = f"https://{self.host}/api/relay/rest/tasks"
    data = json.dumps({ 'context': context, 'message': message }).encode('utf8')
    headers = {
      'Authorization': self._authorization(),
      'Content-Type': 'application/json',
      'Content-Length': len(data)
    }
    req = Request(uri, data=data, headers=headers)
    try:
      response = urlopen(req)
      return response.getcode() == 204
    except HTTPError as error:
      print('Task deliver error: {0}'.format(str(error)))
      return False
