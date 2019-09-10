import os
from signalwire.relay.client import Client

def main():
  project = os.getenv('PROJECT', '')
  token = os.getenv('TOKEN', '')
  client = Client(project=project, token=token)
  client.connect()

main()
