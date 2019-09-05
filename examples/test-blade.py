import asyncio
import signal
import os
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect
from signalwire.blade.connection import Connection
from signalwire.blade.client import Client

def main():
  project = os.getenv('PROJECT', '')
  token = os.getenv('TOKEN', '')
  client = Client(project=project, token=token)
  client.connect()

main()
