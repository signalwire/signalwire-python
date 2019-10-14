from . import BaseResult

class RecordResult(BaseResult):

  @property
  def url(self):
    return self.component.url

  @property
  def duration(self):
    return self.component.duration

  @property
  def size(self):
    return self.component.size
