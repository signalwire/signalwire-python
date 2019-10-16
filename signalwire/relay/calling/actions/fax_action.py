from . import BaseAction
from ..results.fax_result import FaxResult
from ..results.stop_result import StopResult

class FaxAction(BaseAction):

  @property
  def result(self):
    return FaxResult(self.component)

  async def stop(self):
    result = await self.component.stop()
    return StopResult(result)
