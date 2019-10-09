from . import BaseResult

class PlayResult(BaseResult):
  pass

class PlayPauseResult:
  def __init__(self, successful):
    self.successful = successful

class PlayResumeResult:
  def __init__(self, successful):
    self.successful = successful

class PlayVolumeResult:
  def __init__(self, successful):
    self.successful = successful
