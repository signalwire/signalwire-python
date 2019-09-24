from . import BaseResult

class HangupResult(BaseResult):
  def __init__(self, component):
    super().__init__(component)

  @property
  def reason(self):
    return self.component.reason
