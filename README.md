# SignalWire Python SDK

This package wraps the Twilio SDK for use with Signalwire.

[![PyPI version](https://badge.fury.io/py/signalwire.svg)](https://badge.fury.io/py/signalwire)

![Drone CI](https://ci.signalwire.com/api/badges/signalwire/signalwire-python/status.svg)

## Installation

`pip install signalwire`

## Usage

You can find documentation on the [SignalWire website](https://docs.signalwire.com/topics/laml-api/?python#laml-rest-api).

Before you use this library, you will need to create a space on SignalWire.

You can then provide your SignalWire Space URL either via the constructor or by setting the `SIGNALWIRE_SPACE_URL` environment library.

### Make a call

```
from signalwire.rest import Client as signalwire_client

account = "ACXXXXXXXXXXXXXXXXX"
token = "YYYYYYYYYYYYYYYYYY"
client = signalwire_client(account, token, signalwire_space_url = 'example.signalwire.com')

call = client.calls.create(to="+19991231234",
                           from_="+19991231234",
                           url="https://cdn.signalwire.com/default-music/playlist.xml",
                           method="GET")
print(call.sid)
```

### Generate a LAML response

```
from signalwire.voice_response import VoiceResponse

r = VoiceResponse()
r.say("Welcome to SignalWire!")
print(str(r))
```

```
<?xml version="1.0" encoding="utf-8"?>
<Response><Say>Welcome to SignalWire!</Say></Response>
```

## Tests

A `Dockerfile` is provided for your testing convenience.

Run `docker run -it $(docker build -q .)` to execute the specs, or `docker run -it $(docker build -q .) sh` to get a shell with the `signalwire` package installed.

## Licensing

This package is licensed under the MIT license.

Copyright (c) 2018 SignalWire Inc. - see LICENSE.md for details.
