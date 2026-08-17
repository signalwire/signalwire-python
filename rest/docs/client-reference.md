# RestClient Reference

## Constructor

<!-- snippet: no-compile signature-illustration (constructor signature; annotations shown in call form, not a def) -->
```python
RestClient(
    project: str = None,   # SIGNALWIRE_PROJECT_ID
    token: str = None,     # SIGNALWIRE_API_TOKEN
    host: str = None,      # SIGNALWIRE_SPACE
)
```

All parameters fall back to their corresponding environment variables. A `ValueError` is raised if any are missing.

Authentication uses HTTP Basic Auth (`project:token`).

## Namespaces

Every API surface is available as a namespace attribute on the client:

### Fabric API

| Attribute | Description |
|-----------|-------------|
| `client.fabric.swml_scripts` | SWML script resources (CRUD + addresses) |
| `client.fabric.swml_webhooks` | SWML webhook resources |
| `client.fabric.ai_agents` | AI agent resources |
| `client.fabric.relay_applications` | Relay application resources |
| `client.fabric.call_flows` | Call flow resources (+ versions) |
| `client.fabric.conference_rooms` | Conference room resources |
| `client.fabric.freeswitch_connectors` | FreeSWITCH connector resources |
| `client.fabric.subscribers` | Subscriber resources (+ SIP endpoints) |
| `client.fabric.sip_endpoints` | SIP endpoint resources |
| `client.fabric.sip_gateways` | SIP gateway resources |
| `client.fabric.cxml_scripts` | cXML script resources |
| `client.fabric.cxml_webhooks` | cXML webhook resources |
| `client.fabric.cxml_applications` | cXML application resources (no create) |
| `client.fabric.resources` | Generic resource operations |
| `client.fabric.addresses` | Fabric addresses (list/get only) |
| `client.fabric.tokens` | Subscriber/guest/invite/embed token creation |

### Calling API

| Attribute | Description |
|-----------|-------------|
| `client.calling` | REST call control -- 37 commands via POST |

### Relay REST Resources

| Attribute | Description |
|-----------|-------------|
| `client.phone_numbers` | Phone number management (+ search) |
| `client.addresses` | Address management |
| `client.queues` | Queue management (+ members) |
| `client.recordings` | Recording management |
| `client.number_groups` | Number group management (+ memberships) |
| `client.verified_callers` | Verified caller ID management (+ verification flow) |
| `client.sip_profile` | Project SIP profile (get/update) |
| `client.lookup` | Phone number lookup |
| `client.short_codes` | Short code management |
| `client.imported_numbers` | Import external phone numbers |
| `client.mfa` | Multi-factor authentication (SMS/call/verify) |
| `client.registry` | 10DLC brand/campaign registry |

### Other APIs

| Attribute | Description |
|-----------|-------------|
| `client.datasphere` | Datasphere document management and semantic search |
| `client.video` | Video rooms, sessions, recordings, conferences |
| `client.logs` | Message, voice, fax, and conference logs |
| `client.project` | API token management |
| `client.pubsub` | PubSub token creation |
| `client.chat` | Chat token creation |

## Request Options (timeout / retries / abort)

`RequestOptions` tunes the HTTP transport — per-request `timeout`, `retries`
(with `retry_backoff`), the retryable-status set, an `abort_signal`, and extra
`headers`. It can be set at **two levels**:

- **Client default** — pass `request_options=` to the `RestClient` constructor to
  apply it to every call the client makes.
- **Per call** — pass `request_options=` to any resource verb (`list`, `get`,
  `create`, `update`, `delete`, `list_addresses`, and the generated operation /
  command methods) to override the client default for that single call. It is a
  keyword-only argument, extracted by the SDK and never sent in the request body
  or query string.

A per-call value shallow-overrides the client default (only the fields you set
are changed).

<!-- snippet: no-run live REST/HTTP call to a real host (needs credentials/network) -->
```python
from signalwire.rest import RestClient, RequestOptions

# Client-level default: a 10s timeout on every call.
client = RestClient(request_options=RequestOptions(timeout=10.0))

# Per-call override: this one list call retries a transient failure up to twice
# and uses a shorter timeout, without changing the client default.
addresses = client.addresses.list(
    request_options=RequestOptions(timeout=2.0, retries=2)
)

# Works on every resource verb, including create / get and generated methods.
doc = client.datasphere.documents.search(
    query_string="hello",
    request_options=RequestOptions(retries=1),
)
```

Retries are idempotency-aware: `GET`/`PUT`/`DELETE` retry on the full retryable
status set, while `POST`/`PATCH` retry only on throttling responses (429/503),
never on `500`/`502`/`504`, so a non-idempotent write is not silently duplicated.

## Error Handling

```python
from signalwire.rest import SignalWireRestError

try:
    client.fabric.ai_agents.get("bad-id")
except SignalWireRestError as e:
    print(e.status_code)  # 404
    print(e.body)         # {"error": "not found"}
    print(e.url)          # "/api/fabric/resources/ai_agents/bad-id"
    print(e.method)       # "GET"
```

`SignalWireRestError` is raised on any non-2xx HTTP response.

### Error Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP status code |
| `body` | `dict` or `str` | Response body (parsed JSON or raw text) |
| `url` | `str` | Request path |
| `method` | `str` | HTTP method |

## Session Behavior

- A single `requests.Session` is shared across all namespaces for connection pooling.
- Content-Type is always `application/json`.
- User-Agent is `signalwire-agents-python-rest/1.0`.
- DELETE requests returning 204 return an empty dict.
