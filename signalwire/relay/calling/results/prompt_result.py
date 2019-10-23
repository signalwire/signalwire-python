from . import BaseResult

class PromptResult(BaseResult):

  @property
  def prompt_type(self):
    return self.component.prompt_type

  @property
  def result(self):
    return self.component.input

  @property
  def terminator(self):
    return self.component.terminator

  @property
  def confidence(self):
    return self.component.confidence

class PromptVolumeResult:
  def __init__(self, successful):
    self.successful = successful
