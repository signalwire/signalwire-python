# SignalWire Python SDK

This package wraps the Twilio SDK for use with Signalwire.

Refer to [the official Twilio library](https://github.com/twilio/twilio-python) for more examples of usage.

## Installation

`pip install signalwire`

## Usage

```
from signalwire.rest import Client as signalwire_client

account = "ACXXXXXXXXXXXXXXXXX"
token = "YYYYYYYYYYYYYYYYYY"
client = signalwire_client(account, token, signalwire_base_url = 'api.signalwire.com').create

call = client.calls.create(to="9991231234",
                           from_="9991231234",
                           url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")
print(call.sid)
```
