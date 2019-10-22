from .base_fax import BaseFax
from ..constants import Method

class FaxSend(BaseFax):

  def __init__(self, call, document, identity=None, header=None):
    super().__init__(call)
    self._document = document
    self._identity = identity
    self._header = header

  @property
  def method(self):
    return Method.SEND_FAX

  @property
  def payload(self):
    tmp = {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id,
      'document': self._document
    }
    if self._identity:
      tmp['identity'] = self._identity
    if self._header:
      tmp['header_info'] = self._header
    return tmp
