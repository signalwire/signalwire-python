# AI Chat Gateway

A browser-facing proxy so a chat widget never holds a SignalWire API token.

## The problem

A chat widget runs in a page. To reach the AI Chat service it needs
`project_id:api_token` — and that token carries the whole project. Put it in
JavaScript and every visitor can read it, run up turns on your project, and
each of those turns bills you.

## The shape

```
browser ──(publishable key)──▶ your app ──(project:token)──▶ chat service
```

The widget learns exactly two things: the gateway's URL and a publishable key.
Not the project, not the space, not the token, and not which agent config runs
— the gateway injects `config_url` itself, so a key can only ever reach the one
script it was issued for.

If you already run an agent, you already run the server this mounts on.

## Quick start

```python
from signalwire.ai_chat import ChatGateway

gateway = ChatGateway(
    config_url="https://my-agent.example.com/swml",   # the one script this key reaches
    key="pk_live_...",                                # what the widget carries
    allowed_origins=["https://shop.example.com"],     # localhost is always allowed
)

agent.get_app().include_router(gateway.router(), prefix="/chat")
```

Credentials come from `SIGNALWIRE_PROJECT_ID` / `SIGNALWIRE_API_TOKEN` /
`SIGNALWIRE_SPACE`, the same as `AIChatClient`. Pass `client=` to supply your
own.

It mounts on any FastAPI app, not just an agent:

```python
app = FastAPI()
app.include_router(gateway.router(), prefix="/chat")
```

## The wire

One endpoint. `POST {prefix}/` with the key in `Authorization: Bearer`.

**First message** — no handle, so the gateway mints a conversation:

```http
POST /chat/
Authorization: Bearer pk_live_...
{"message": "hello"}
```

```http
200 OK
X-Chat-Handle: eyJ...abc.def...

{"jsonrpc": "2.0", "result": {"response": "Hi! How can I help?"}, "id": "req-1"}
```

Keep `X-Chat-Handle` and send it on every subsequent message:

```http
POST /chat/
{"handle": "eyJ...abc.def...", "message": "where is my order?"}
```

**Ending:**

```http
POST /chat/
{"method": "end", "handle": "eyJ...abc.def..."}
```
```json
{"status": "ended"}
```

Two notes on the response body:

- **It is the service's JSON-RPC envelope, relayed verbatim.** A failed turn
  arrives as `{"error": {"code": …, "message": …}}` under **HTTP 200** — the
  service commits `200` before the turn's outcome is known. Check for `error`
  in the body, not the status code.
- **It may begin with whitespace.** See [Streaming](#streaming).

Only `chat` and `end` are accepted. Anything else is a `400`.

## What a stolen key can do

Design for this, because a publishable key is public by definition.

**It cannot read anything.** `chat_log` is not exposed, and conversation
handles are HMAC-signed by the gateway, so ids cannot be guessed or
enumerated — a caller can only present handles the gateway issued.

**It can talk, and talking costs money.** That is the real exposure, which is
why the caps are the primary control rather than a nicety:

| | default | bounds |
|---|---|---|
| `max_new_conversations` | 60 / minute | how many conversations can exist |
| `max_turns` | 200 / conversation | how long each one runs |

The first is the one that matters most. A leaked key does not hammer a single
conversation — it mints thousands of one-turn ones, and **every one of those
bills its opening turn**. Rate-limiting turns alone would not catch that.

Counters live in the serving process. Behind several replicas each keeps its
own, so the effective cap multiplies by replica count. Set them with that in
mind, or put a shared limiter in front.

## Origins

`allowed_origins` is a list; **localhost is always allowed** so local
development works unconfigured, and anything else must be listed, so nothing
ships open by accident.

Be clear-eyed about what this buys. It stops a key pasted into someone else's
page, because a browser sends their origin and the gateway refuses it. It does
not stop anyone using curl, who simply omits the header. Treat it as leak
containment, not access control — the caps above are what actually bound your
exposure.

The same list drives CORS: allowed origins get `Access-Control-Allow-Origin`,
`Access-Control-Expose-Headers: X-Chat-Handle`, and a preflight response.

## Handles

Signed with an HMAC secret, carrying the conversation id and an expiry
(`handle_ttl`, 24h by default).

Set `secret=` (or `SIGNALWIRE_CHAT_GATEWAY_SECRET`) explicitly if you run more
than one replica or restart often — a random per-process secret means
outstanding handles stop working on restart, and a handle minted by one
replica is refused by another.

Dropping `chat_log` is a deliberate trade: the widget cannot rehydrate a
transcript after a page refresh. Keep it client-side, or start fresh.

## Streaming

The gateway relays the response body **unbuffered**.

The chat service pads a slow turn with keepalive whitespace so intermediaries
do not sever the connection mid-turn. That padding is valid JSON leading
whitespace, so `JSON.parse` is unaffected — but only if the relay forwards
bytes instead of decoding them. A gateway that awaited the whole body would
swallow the padding and recreate the very timeout it exists to prevent, this
time inside your own stack where nobody thinks to look.

This is why a newly minted handle comes back in a **header**: headers are sent
before the body, so the widget gets its handle immediately without anything
waiting on the turn to finish.

If you put your own proxy in front of the gateway, make sure it does not
buffer either.

## Rotating a key

There is no expiry on the key itself — publishable keys live in static pages,
and a TTL means the widget silently dies at some point. Rotate on demand
instead: construct the gateway with a new `key` and redeploy. Change `secret`
at the same time if you want outstanding handles invalidated too.

## Reference

```python
ChatGateway(
    *,
    config_url: str,                       # required; what the key is scoped to
    key: str | None = None,                # SIGNALWIRE_CHAT_GATEWAY_KEY, else generated
    allowed_origins: list[str] = (),       # localhost always allowed
    client: AIChatClient | None = None,    # built from env if omitted
    secret: bytes | str | None = None,     # SIGNALWIRE_CHAT_GATEWAY_SECRET, else random
    handle_ttl: int = 86400,
    max_new_conversations: int = 60,
    max_turns: int = 200,
    window_seconds: int = 60,
)
```

| method | purpose |
|---|---|
| `router()` | `APIRouter` to `include_router` |
| `mint_handle(conversation_id=None)` | issue a signed handle server-side |
| `read_handle(handle)` | conversation id, or raise `GatewayRejection` |
| `prepare(body, *, origin, key)` | validate and build the upstream call — the framework-agnostic core, if you are not using FastAPI |
| `close()` | close the client, if the gateway built it |

`GatewayRejection` carries `.status` and `.reason`. Reasons are deliberately
coarse: anything finer would let a caller map the caps and the allowlist by
probing.
