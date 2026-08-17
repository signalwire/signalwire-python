# EXAMPLES_RUN_ALLOW.md — examples excused from EXAMPLES-RUN

The EXAMPLES-RUN gate runs each shipped example against a mock SignalWire
environment and fails on a load/startup crash. Examples listed here legitimately
cannot run in that harness — they require real third-party credentials, real
network endpoints, an optional deployment-only dependency, or interactive input.
Each entry: `- <path> — reason (approver, date)`. This is NOT a place to hide a
real example bug; every entry names a concrete external requirement.

- examples/joke_agent.py — requires a real API_NINJAS_KEY (jokes API); example sys.exit(1)s without it by design (mike, 2026-07-08)
- examples/joke_skill_demo.py — same: requires real API_NINJAS_KEY for the joke skill (mike, 2026-07-08)
- examples/bedrock_with_skills.py — weather_api skill requires a real weather-provider api_key (mike, 2026-07-08)
- examples/datasphere_serverless_env_demo.py — requires DATASPHERE_* env (real Datasphere index/creds) (mike, 2026-07-08)
- examples/datasphere_webhook_env_demo.py — requires DATASPHERE_* env (real Datasphere index/creds) (mike, 2026-07-08)
- examples/mcp_gateway_demo.py — mcp_gateway skill setup requires a reachable external MCP gateway (mike, 2026-07-08)
- examples/quickstart_rest.py — issues a real fabric.ai_agents.create() REST call on load; needs real SignalWire project creds (401 against mock) (mike, 2026-07-08)
- examples/lambda_agent.py — requires the optional `mangum` AWS-Lambda adapter (deployment-only, not a base dependency) (mike, 2026-07-08)
- examples/swml_service_example.py — interactive: calls input() for a menu choice; cannot run headless (EOFError) (mike, 2026-07-08)
- relay/examples/relay_dial_and_play.py — drives an outbound RELAY call via a direct `await client.connect()` (no reconnect loop), which opens a real `wss://` RELAY WebSocket; the EXAMPLES-RUN harness starts only the REST mock (no RELAY WS endpoint), so connect() raises immediately. Needs a real SignalWire RELAY endpoint (mike, 2026-07-23)
