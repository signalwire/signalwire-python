from signalwire.rest import Client as signalwire_client

account = "YOURACCOUNT"
token = "YOURTOKEN"
client = signalwire_client(account, token, signalwire_space_url = 'yourspace.signalwire.com')

message = client.messages.create(
  to="+1xxx",
  from_="+1yyy", #must be a number in your Signalwire account
  body="Hello, how are you?"
)

print(message)
