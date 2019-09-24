from signalwire.relay.calling import Calling, Call
from signalwire.tests import MockedConnection

def test_add_call(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance)
  c2 = Call(calling=instance)
  c3 = Call(calling=instance)
  assert len(instance.calls) == 3

def test_remove_call(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance)
  instance.remove_call(c1)
  assert len(instance.calls) == 0

def test_get_call_by_id(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance, **{ 'call_id': '1234' })
  assert instance._get_call_by_id('1234') is c1

def test_get_call_by_tag(relay_client):
  instance = Calling(relay_client)
  c1 = Call(calling=instance, **{ 'call_id': '1234' })
  assert instance._get_call_by_tag(c1.tag) is c1
