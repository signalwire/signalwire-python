from abc import ABC
from ..components import BaseComponent

class BaseResult(ABC):
  def __init__(self, component: BaseComponent):
    self.component = component

  @property
  def successful(self):
    return self.component.successful

  @property
  def event(self):
    return self.component.event
