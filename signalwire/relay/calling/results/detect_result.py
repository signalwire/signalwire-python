from . import BaseResult

class DetectResult(BaseResult):

  @property
  def detect_type(self):
    return self.component.detect_type

  @property
  def result(self):
    return self.component.result
