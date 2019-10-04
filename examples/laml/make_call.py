from signalwire.rest import Client as signalwire_client

account = "YOURACCOUNT"
token = "YOURTOKEN"
client = signalwire_client(account, token, signalwire_space_url = 'yourspace.signalwire.com')

call = client.calls.create(
  to="+1xxx",
  from_="+1yyy", #must be a number in your Signalwire account
  url="https://cdn.signalwire.com/default-music/playlist.xml",
  method="GET"
)

print(call)

# get the latest 5 calls and print their statuses
callrec = client.calls.list()
for record in callrec[:5]:
    print(record.sid)
    print(record.status)
