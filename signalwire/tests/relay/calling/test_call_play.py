import asyncio
import json
import pytest
from unittest.mock import Mock

async def _fire(calling, notification):
  calling.notification_handler(notification)

def test_play_events(relay_call):
  mock = Mock()
  relay_call.on('play.stateChange', mock)
  relay_call.on('play.finished', mock)
  payload = json.loads('{"event_type":"calling.call.play","params":{"control_id":"control-id","call_id":"call-id","node_id":"node-id","state":"finished"}}')
  relay_call.calling.notification_handler(payload)
  assert mock.call_count == 2
