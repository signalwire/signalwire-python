from . import BaseAction
from ..results.play_result import PlayResult

class PlayAction(BaseAction):

  @property
  def result(self):
    return PlayResult(self.component)

  def stop(self):
    return self.component.stop()

  def pause(self):
    # TODO:
    return self.component.pause()

  def resume(self):
    # TODO:
    return self.component.resume()
