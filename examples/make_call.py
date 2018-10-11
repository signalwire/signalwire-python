from signalwire.rest import Client as signalwire_client

account = "YOURACCOUNT"
token = "YOURTOKEN"
client = signalwire_client(account, token, signalwire_base_url = 'https://yourspace.signalwire.com')

call = client.calls.create(
  to="140498765432",
  from_="120823456789", #must be a number in your Signalwire account
  url="https://s3.us-east-2.amazonaws.com/signalwire-frontend/default-music/playlist.xml"
)

