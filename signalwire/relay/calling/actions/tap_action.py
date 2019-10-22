from . import BaseAction
from ..results.tap_result import TapResult
from ..results.stop_result import StopResult

class TapAction(BaseAction):

  @property
  def result(self):
    return TapResult(self.component)

  @property
  def source_device(self):
    return self.component.source_device

  async def stop(self):
    result = await self.component.stop()
    return StopResult(result)
