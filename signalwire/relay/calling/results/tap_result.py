from . import BaseResult

class TapResult(BaseResult):

  @property
  def tap(self):
    return self.component.tap

  @property
  def source_device(self):
    return self.component.source_device

  @property
  def destination_device(self):
    return self.component.device
