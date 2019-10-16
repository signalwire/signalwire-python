from . import BaseResult

class FaxResult(BaseResult):

  @property
  def direction(self):
    return self.component.direction

  @property
  def identity(self):
    return self.component.identity

  @property
  def remote_identity(self):
    return self.component.remote_identity

  @property
  def document(self):
    return self.component.document

  @property
  def pages(self):
    return self.component.pages
