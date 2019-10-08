from . import BaseAction
from ..results.connect_result import ConnectResult

class ConnectAction(BaseAction):

  @property
  def result(self):
    return ConnectResult(self.component)
