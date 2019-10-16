from . import BaseComponent
from ..constants import Notification, CallFaxState
from ...event import Event
from .decorators import stoppable

@stoppable
class BaseFax(BaseComponent):

  def __init__(self, call):
    super().__init__(call)
    self.direction = None
    self.identity = None
    self.remote_identity = None
    self.document = None
    self.pages = None

  @property
  def event_type(self):
    return Notification.FAX

  def notification_handler(self, params):
    try:
      fax = params['fax']
      self.state = fax['type']
    except KeyError:
      return

    self.completed = self.state != CallFaxState.PAGE
    if self.completed:
      self.unregister()
      self.event = Event(self.state, fax)
      self.successful = fax['params'].get('success', False)
      if self.successful:
        self.direction = fax['params'].get('direction', None)
        self.identity = fax['params'].get('identity', None)
        self.remote_identity = fax['params'].get('remote_identity', None)
        self.document = fax['params'].get('document', None)
        self.pages = fax['params'].get('pages', None)
      if self.has_future():
        self._future.set_result(True)
