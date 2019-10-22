from .base_fax import BaseFax
from ..constants import Method

class FaxReceive(BaseFax):

  @property
  def method(self):
    return Method.RECEIVE_FAX

  @property
  def payload(self):
    return {
      'node_id': self.call.node_id,
      'call_id': self.call.id,
      'control_id': self.control_id
    }
