import os
from signalwire.relay.client import Client

def ready(client):
  print('Client ready!')
  print(client)
  pass

def main():
  project = os.getenv('PROJECT', '')
  token = os.getenv('TOKEN', '')
  client = Client(project=project, token=token)
  client.on('ready', ready)
  client.connect()

main()
