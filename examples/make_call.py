from signalwire.rest import Client as signalwire_client

account = "YOURACCOUNT"
token = "YOURTOKEN"
client = signalwire_client(account, token, signalwire_base_url = 'https://yourspace.signalwire.com')

call = client.calls.create(
  to="140498765432",
  from_="120823456789", #must be a number in your Signalwire account
  url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
)

