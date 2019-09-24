import json
import pytest
from signalwire.relay.calling import Call

@pytest.fixture()
def relay_call(relay_calling):
  params = json.loads('{"call_state":"created","context":"office","device":{"type":"phone","params":{"from_number":"+12029999999","to_number":"+12028888888"}},"direction":"inbound","call_id":"call-id","node_id":"node-id"}')
  return Call(calling=relay_calling, **params)

def test_init_options(relay_call):
  assert relay_call.id == 'call-id'
  assert relay_call.node_id == 'node-id'
  assert relay_call.call_type == 'phone'
  assert relay_call.from_number == '+12029999999'
  assert relay_call.to_number == '+12028888888'
  assert relay_call.state == 'created'
  assert relay_call.context == 'office'
  assert relay_call.timeout is None

def test_device(relay_call):
  assert relay_call.device == {'type':'phone','params':{'from_number':'+12029999999','to_number':'+12028888888'}}
