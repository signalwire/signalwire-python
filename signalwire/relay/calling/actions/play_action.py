from . import BaseAction
from ..results.play_result import PlayResult, PlayPauseResult, PlayResumeResult
from ..results.stop_result import StopResult

class PlayAction(BaseAction):

  @property
  def result(self):
    return PlayResult(self.component)

  def stop(self):
    result = await self.component.stop()
    return StopResult(result)

  async def pause(self):
    result = await self.component.pause()
    return PlayPauseResult(result)

  async def resume(self):
    result = await self.component.resume()
    return PlayResumeResult(result)
