import asyncio
import os
from signalwire.relay.client import Client

async def inbound_call(call):
  result = await call.answer()
  if result.successful:
    print('Inbound call answered successful')
    await asyncio.sleep(5)
    hangup = await call.hangup()
    if hangup.successful:
      print('Call hangup')
    else:
      print('Call hangup failed')
  else:
    print('Inbound call failed or not answered')

async def ready(client):
  print('Client ready!')
  await client.calling.receive(['home', 'office'], inbound_call)
  # call = client.calling.new_call(from_number='+1xxx', to_number='+1yyy')
  # result = await call.dial()
  # if result.successful:
  #   print('Outbound call answered successful')
  # else:
  #   print('Outbound call failed or not answered')

def main():
  project = os.getenv('PROJECT', '')
  token = os.getenv('TOKEN', '')
  client = Client(project=project, token=token, host='relay.swire.io')
  client.on('ready', ready)
  client.connect()

main()
