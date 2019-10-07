from abc import ABC
from ..components import BaseComponent

class BaseAction(ABC):
  def __init__(self, component: BaseComponent):
    self.component = component

  @property
  def control_id(self):
    return self.component.control_id

  @property
  def payload(self):
    return self.component.payload

  @property
  def completed(self):
    return self.component.completed

  @property
  def state(self):
    return self.component.state
