import asyncio
import signal
import os
from signalwire.blade.messages.message import Message
from signalwire.blade.messages.connect import Connect
from signalwire.blade.connection import Connection
from signalwire.blade.client import Client

def main():
  project = os.getenv('PROJECT', '64ae1770-0ce3-43f0-b016-28eb668416bf')
  token = os.getenv('TOKEN', 'PT4fb17881c426c5016d67e66749bd0249064be88641876476')
  client = Client(project=project, token=token)
  client.connect()

main()
