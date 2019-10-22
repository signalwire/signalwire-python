from . import BaseAction
from ..results.send_digits_result import SendDigitsResult

class SendDigitsAction(BaseAction):

  @property
  def result(self):
    return SendDigitsResult(self.component)
