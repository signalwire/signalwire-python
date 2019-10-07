from . import BaseResult

class ConnectResult(BaseResult):
  def __init__(self, component):
    super().__init__(component)

  @property
  def call(self):
    return self.component.call.peer
