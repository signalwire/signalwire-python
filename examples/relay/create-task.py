import asyncio
import os
from signalwire.relay.task import Task

project = os.getenv('PROJECT', '')
token = os.getenv('TOKEN', '')
task = Task(project=project, token=token)
success = task.deliver('office', { 'key': 'value', 'data': 'random stuff' })
if success:
  print('Task delivered')
else:
  print('Task NOT delivered')
