from . import BaseAction
from ..results.detect_result import DetectResult
from ..results.stop_result import StopResult

class DetectAction(BaseAction):

  @property
  def result(self):
    return DetectResult(self.component)

  async def stop(self):
    result = await self.component.stop()
    return StopResult(result)
