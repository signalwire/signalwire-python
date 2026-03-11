# SignalWire RELAY Client Implementation Guide

This document is for AI coding agents implementing a RELAY client in any language. It describes the wire protocol, correlation mechanisms, and critical pitfalls that are not obvious from the spec alone.

## Protocol Overview

RELAY uses JSON-RPC 2.0 over WebSocket. The server is at `wss://<host>` (no path). All communication is async — you send requests, get responses matched by `id`, and receive server-pushed events via `signalwire.event`.

## Authentication

```json
{
  "jsonrpc": "2.0",
  "id": "<uuid>",
  "method": "signalwire.connect",
  "params": {
    "version": {"major": 2, "minor": 0, "revision": 0},
    "agent": "your-sdk-name/1.0",
    "event_acks": true,
    "authentication": {"project": "<project_id>", "token": "<token>"},
    "contexts": ["office", "support"]
  }
}
```

The response contains a `protocol` string — save it and send it back on reconnect to resume the session.

## Four Correlation Mechanisms

Every method uses one or more of these to bind requests to responses and events. Getting these wrong is the #1 source of bugs.

### 1. JSON-RPC `id` (ALL methods)

Every request has a UUID `id`. The server responds with the same `id`. This is how you match RPC responses to pending requests.

```
Client → {"jsonrpc":"2.0", "id":"abc-123", "method":"calling.answer", "params":{...}}
Server → {"jsonrpc":"2.0", "id":"abc-123", "result":{"code":"200", "message":"Answered"}}
```

Implementation: maintain a `pending: Map<string, Future>` keyed by request `id`.

### 2. `call_id` routing (all call-level methods)

Every call method sends `node_id` + `call_id` in params. Events come back with `call_id` in their params. Route events to the correct Call object by `call_id`.

```
Client → {"method":"calling.play", "params":{"node_id":"n1", "call_id":"c1", "control_id":"ctl1", ...}}
Server event → {"method":"signalwire.event", "params":{"event_type":"calling.call.play", "params":{"call_id":"c1", "control_id":"ctl1", "state":"finished"}}}
```

Implementation: maintain a `calls: Map<string, Call>` keyed by `call_id`.

### 3. `control_id` action tracking (12 methods)

Methods that start long-running operations (play, record, detect, etc.) take a client-generated `control_id`. The server echoes it back in events. Multiple actions can run concurrently on the same call — `control_id` disambiguates.

Implementation: each Call maintains `actions: Map<string, Action>` keyed by `control_id`.

### 4. `tag` correlation (dial only)

**CRITICAL**: `calling.dial` is the only method where the RPC response does NOT contain a `call_id`. The response is just `{"code":"200", "message":"Dialing"}`. The real `call_id` and `node_id` arrive asynchronously via events matched by `tag`.

Implementation: maintain `pending_dials: Map<string, Future<Call>>` keyed by `tag`.

## Method Categories

### Simple fire-and-response (no async tracking)

These methods send an RPC, get a response with `code`/`message`, and are done. No control_id, no ongoing events to track.

| Method | RPC | Response |
|--------|-----|----------|
| `answer` | `calling.answer` | `{"code":"200", "message":"Answered"}` |
| `end` | `calling.end` | `{"code":"200", "message":"Disconnecting call"}` |
| `pass` | `calling.pass` | `{"code":"200", "message":"Passing call"}` |
| `connect` | `calling.connect` | `{"code":"200", "message":"connecting"}` |
| `disconnect` | `calling.disconnect` | `{"code":"200", "message":"Disconnecting"}` |
| `hold` | `calling.hold` | `{"code":"200", "message":"Call on hold"}` |
| `unhold` | `calling.unhold` | `{"code":"200", "message":"Call off hold"}` |
| `denoise` | `calling.denoise` | `{"code":"200", "message":"Denoiser on"}` |
| `denoise.stop` | `calling.denoise.stop` | `{"code":"200", "message":"Denoiser off"}` |
| `transfer` | `calling.transfer` | `{"code":"200", "message":"Transferring"}` |
| `join_conference` | `calling.join_conference` | `{"code":"200", "message":"Joining conference"}` |
| `leave_conference` | `calling.leave_conference` | `{"code":"200", "message":"Leaving conference"}` |
| `echo` | `calling.echo` | `{"code":"200", "message":"Echo started"}` |
| `bind_digit` | `calling.bind_digit` | `{"code":"200", "message":"Digit binding created"}` |
| `clear_digit_bindings` | `calling.clear_digit_bindings` | `{"code":"200", "message":"Digit bindings cleared"}` |
| `live_transcribe` | `calling.live_transcribe` | `{"code":"200", "message":"Live transcription started"}` |
| `live_translate` | `calling.live_translate` | `{"code":"200", "message":"Live translation started"}` |
| `join_room` | `calling.join_room` | `{"code":"200", "message":"Joining room"}` |
| `leave_room` | `calling.leave_room` | `{"code":"200", "message":"Leaving room"}` |
| `amazon_bedrock` | `calling.amazon_bedrock` | `{"code":"200", "message":"AI started"}` |
| `ai_message` | `calling.ai_message` | `{"code":"200", "message":"Message sent"}` |
| `ai_hold` | `calling.ai_hold` | `{"code":"200", "message":"AI on hold"}` |
| `ai_unhold` | `calling.ai_unhold` | `{"code":"200", "message":"AI resumed"}` |
| `user_event` | `calling.user_event` | `{"code":"200", "message":"Event sent"}` |
| `queue.enter` | `calling.queue.enter` | `{"code":"200", "message":"Entering Queue"}` |
| `queue.leave` | `calling.queue.leave` | `{"code":"200", "message":"Leaving Queue"}` |
| `refer` | `calling.refer` | `{"code":"200", "message":"Starting SIP REFER"}` |
| `send_digits` | `calling.send_digits` | `{"code":"200", "message":"Sending Digits"}` |

Note: `connect`, `refer`, `send_digits` etc. DO produce async events (`calling.call.connect`, `calling.call.refer`, `calling.call.send_digits`) but these route normally by `call_id`. You don't need special tracking — just the standard event dispatch.

### control_id action methods (require action tracking)

These methods start a long-running operation. The client generates a `control_id` UUID, sends it in the request, and the server echoes it back in all related events. You MUST track these as Action objects to support `stop()`, `pause()`, `resume()`, `wait()`.

| Method | RPC | Event Type | Terminal States |
|--------|-----|------------|-----------------|
| `play` | `calling.play` | `calling.call.play` | `finished`, `error` |
| `record` | `calling.record` | `calling.call.record` | `finished`, `no_input` |
| `detect` | `calling.detect` | `calling.call.detect` | `finished`, `error` |
| `collect` | `calling.collect` | `calling.call.collect` | `finished`, `error`, `no_input`, `no_match` |
| `play_and_collect` | `calling.play_and_collect` | `calling.call.collect` | `finished`, `error`, `no_input`, `no_match` |
| `pay` | `calling.pay` | `calling.call.pay` | `finished`, `error` |
| `send_fax` | `calling.send_fax` | `calling.call.fax` | `finished`, `error` |
| `receive_fax` | `calling.receive_fax` | `calling.call.fax` | `finished`, `error` |
| `tap` | `calling.tap` | `calling.call.tap` | `finished` |
| `stream` | `calling.stream` | `calling.call.stream` | `finished` |
| `transcribe` | `calling.transcribe` | `calling.call.transcribe` | `finished` |
| `ai` | `calling.ai` | N/A (ends on call end or stop) | `finished`, `error` |

Action sub-commands (these reference an existing `control_id`):
- `play.stop`, `play.pause`, `play.resume`, `play.volume`
- `record.stop`, `record.pause`, `record.resume`
- `detect.stop`
- `collect.stop`, `collect.start_input_timers`
- `play_and_collect.stop`, `play_and_collect.volume`
- `pay.stop`
- `send_fax.stop`, `receive_fax.stop`
- `tap.stop`
- `stream.stop`
- `transcribe.stop`
- `ai.stop`

#### play_and_collect gotcha

`play_and_collect` shares one `control_id` across both the play and collect phases. Events arrive as BOTH `calling.call.play` (for play state) and `calling.call.collect` (for collect result). Your CollectAction must filter by event_type — only resolve on `calling.call.collect` events, NOT on `calling.call.play` events with `state: finished` (that just means playback ended, not that input was collected).

#### detect gotcha

`detect` delivers results continuously via `calling.call.detect` events with a `detect` object. A detect action should resolve on the FIRST meaningful result (e.g., `HUMAN`, `MACHINE`, `CED`, digit) OR on terminal states `finished`/`error`. Don't wait only for `finished` — the useful data comes in intermediate events.

### tag-based methods (dial)

**This is where most implementations break.**

#### calling.dial — the async dance

```
Client → {"method":"calling.dial", "params":{"tag":"my-tag-123", "devices":[[...]]}}
Server → {"result":{"code":"200", "message":"Dialing"}}   ← NO call_id here!
```

After the RPC response, the server sends a sequence of events:

1. **`calling.call.state`** events for each call leg (one per device being dialed):
```json
{"event_type":"calling.call.state", "params":{
  "call_id":"leg-uuid-1", "node_id":"node-uuid", "tag":"my-tag-123",
  "call_state":"created", "device":{...}
}}
```
Then `ringing`, then `answered` or `ended` for each leg.

2. **`calling.call.dial`** event when the dial operation completes:
```json
{"event_type":"calling.call.dial", "params":{
  "node_id":"node-uuid",
  "tag":"my-tag-123",
  "dial_state":"answered",
  "call":{
    "call_id":"winner-uuid",
    "node_id":"node-uuid",
    "tag":"my-tag-123",
    "device":{...},
    "dial_winner": true
  }
}}
```

**CRITICAL DETAILS:**
- The `calling.call.dial` event has NO top-level `call_id` in params. The call info is nested inside `params.call.call_id`.
- `dial_state` values: `dialing` (progress), `answered` (success), `failed` (all legs failed).
- With parallel dialing, multiple call legs are created. Each gets `calling.call.state` events. Only the winner appears in the `calling.call.dial` event with `dial_state: "answered"`. Losers get `calling.call.state` with `call_state: "ended"`.

#### Correct dial() implementation

```python
async def dial(devices, tag=None, timeout=120):
    tag = tag or generate_uuid()

    # 1. Register pending dial BEFORE sending RPC
    future = create_future()
    pending_dials[tag] = future

    # 2. Send the RPC — response is just {"code":"200","message":"Dialing"}
    await execute("calling.dial", {"tag": tag, "devices": devices})

    # 3. Wait for calling.call.dial event to resolve the future
    try:
        call = await wait_for(future, timeout=timeout)
        return call
    finally:
        pending_dials.pop(tag)
```

#### Event routing during dial

Your event handler needs three special cases:

```python
def handle_event(payload):
    event_type = payload["event_type"]
    event_params = payload["params"]
    call_id = event_params.get("call_id", "")

    # 1. Inbound call
    if event_type == "calling.call.receive":
        handle_inbound(payload)
        return

    # 2. Dial completion — call_id is NESTED at params.call.call_id
    if event_type == "calling.call.dial":
        tag = event_params.get("tag", "")
        dial_state = event_params.get("dial_state", "")
        call_info = event_params.get("call", {})
        future = pending_dials.get(tag)
        if future:
            if dial_state == "answered":
                call = find_or_create_call(call_info)
                future.resolve(call)
            elif dial_state == "failed":
                future.reject(Error("Dial failed"))
        return

    # 3. State events during dial — call not registered yet
    if event_type == "calling.call.state":
        tag = event_params.get("tag", "")
        if tag in pending_dials and call_id not in calls:
            # Create the Call object so events route correctly
            register_dial_leg(tag, event_params)
        # Fall through to normal routing

    # 4. Normal routing by call_id
    call = calls.get(call_id)
    if call:
        call.dispatch_event(payload)
        if call.state == "ended":
            calls.pop(call_id)
```

### calling.begin (DEPRECATED)

Unlike `calling.dial`, the deprecated `calling.begin` DOES return `call_id` and `node_id` in the response:
```json
{"code":"200", "message":"Call started", "call_id":"<UUID>", "node_id":"<UUID>"}
```
Do NOT assume `calling.dial` works the same way. It doesn't.

## Event ACK

The server expects an acknowledgment for every `signalwire.event`:
```json
{"jsonrpc":"2.0", "id":"<event_msg_id>", "result":{}}
```
Send this immediately when you receive the event, before processing it.

## Server Pings

The server sends `signalwire.ping` periodically. Respond with:
```json
{"jsonrpc":"2.0", "id":"<ping_msg_id>", "result":{}}
```

## Error Code Handling

The calling API always returns results with `code` and `message`. The code is a STRING, not an integer.

- Any `2xx` code = success
- `404` = call does not exist
- `410` = call existed but is gone
- `409` = conflict (call already connected, controlled by another client)

### Call-gone handling (404/410)

When a caller hangs up, the server destroys the call. If your client tries to send a command (play, record, etc.) after the caller hung up but before you received the `calling.call.state ended` event, you get a 404 or 410 error. **This is normal telephony flow, not an exceptional condition.**

Handle it gracefully: log it and return an empty result instead of raising an exception. This avoids noisy errors in production when callers hang up mid-IVR.

```python
async def execute_on_call(method, params):
    try:
        return await execute(f"calling.{method}", params)
    except RelayError as e:
        if e.code in (404, 410):
            log.info(f"Call gone during {method}")
            return {}
        raise
```

Also: if an action (play, record, etc.) gets a call-gone response, resolve the action's Future immediately so `action.wait()` doesn't hang forever.

## Event Structure Reference

All events arrive as:
```json
{
  "jsonrpc": "2.0",
  "method": "signalwire.event",
  "id": "<msg_id>",
  "params": {
    "event_type": "calling.call.play",
    "timestamp": 123457.1234,
    "params": {
      "call_id": "...",
      "control_id": "...",
      "state": "finished"
    }
  }
}
```

Note the nested `params.params` structure. The outer `params` has `event_type`, the inner `params` has event-specific data like `call_id`, `control_id`, `state`.

### Events with non-standard structure

| Event | Gotcha |
|-------|--------|
| `calling.call.dial` | No top-level `call_id`. Has `tag`, `dial_state`, and `call` object containing `call_id`. |
| `calling.conference` | Uses `conference_id` instead of `call_id` for conference-level events. Participant events DO have `call_id`. |
| `calling.call.detect` | Results are in `detect.params.event`, not in a `state` field. Terminal state is `finished`. |
| `calling.call.collect` | Result object has `type` (digit/speech/error/no_input/no_match) and `params`. |
| `calling.call.record` | `url`, `duration`, `size` may be at top level OR nested inside `record` object. Check both. |

## Reconnection

On WebSocket disconnect:
1. Reject all pending request Futures
2. Reject all pending dial Futures
3. Wait with exponential backoff (1s → 2s → 4s → ... → 30s max)
4. Reconnect and re-authenticate with `signalwire.connect`, sending the previous `protocol` string
5. Flush any queued requests

Call objects survive reconnect — the server tracks them by `call_id` across connections.

## Architecture Checklist

- [ ] `pending` map: request `id` → Future (for RPC response matching)
- [ ] `calls` map: `call_id` → Call (for event routing)
- [ ] Each Call has `actions` map: `control_id` → Action (for action event routing)
- [ ] `pending_dials` map: `tag` → Future<Call> (for dial event matching)
- [ ] Event ACK sent for every `signalwire.event`
- [ ] Pong sent for every `signalwire.ping`
- [ ] 404/410 errors handled gracefully (call-gone, not exceptional)
- [ ] `calling.call.dial` events routed by `tag`, not `call_id`
- [ ] `calling.call.state` events during dial create Call objects before dial completes
- [ ] `play_and_collect` CollectAction filters by event_type, ignores play events
- [ ] Auto-reconnect with exponential backoff
- [ ] All pending futures cleaned up on disconnect
