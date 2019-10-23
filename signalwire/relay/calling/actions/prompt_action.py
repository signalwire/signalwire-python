from . import BaseAction
from ..results.prompt_result import PromptResult, PromptVolumeResult
from ..results.stop_result import StopResult

class PromptAction(BaseAction):

  @property
  def result(self):
    return PromptResult(self.component)

  async def stop(self):
    result = await self.component.stop()
    return StopResult(result)

  async def volume(self, value):
    result = await self.component.volume(value)
    return PromptVolumeResult(result)
