from . import BaseAction
from ..results.record_result import RecordResult
from ..results.stop_result import StopResult

class RecordAction(BaseAction):

  @property
  def result(self):
    return RecordResult(self.component)

  @property
  def url(self):
    return self.component.url

  async def stop(self):
    result = await self.component.stop()
    return StopResult(result)
