# REST coverage — signalwire-python accepted SDK gaps

Canonical REST routes that the **Python SDK** does not implement, so they cannot
reach success+error coverage here. These are the per-port half of the
`REST-COVERAGE` allowlist (type `sdk-gap`); the universal gaps (spec artifacts,
routing collisions) live in `porting-sdk/REST_COVERAGE_BASELINE.md` and are NOT
repeated here.

Format: `<endpoint_id>: sdk-gap — <rationale>`. Each entry is a contract for why
Python doesn't cover it. If a method is later added, the route becomes coverable
and the checker fails on the now-stale entry until it's removed — write the test
and delete the line together.

These 18 gaps were surfaced by the full-coverage build (task #56) and parked for
later review per the maintainer's call; they are not yet decided as won't-fix.

## fabric — dialogflow_agents resource not wired on FabricNamespace

fabric.list_dialogflow_agents: sdk-gap — no `dialogflow_agents` attribute on FabricNamespace; resource is entirely unwired in rest/namespaces/fabric.py.
fabric.get_dialogflow_agent: sdk-gap — no `dialogflow_agents` resource (see above).
fabric.update_dialogflow_agent: sdk-gap — no `dialogflow_agents` resource (PUT update).
fabric.delete_dialogflow_agent: sdk-gap — no `dialogflow_agents` resource.
fabric.list_dialogflow_agent_addresses: sdk-gap — no `dialogflow_agents` resource.

## relay-rest — SIP endpoints + domain applications have no relay-rest namespace

relay-rest.list_sip_endpoints: sdk-gap — no SDK namespace for `/api/relay/rest/endpoints/sip`; SDK exposes SIP endpoints under the Fabric base path instead (likely intentional Fabric supersession).
relay-rest.create_sip_endpoint: sdk-gap — see above (no relay-rest SIP endpoint namespace).
relay-rest.retrieve_sip_endpoint: sdk-gap — see above.
relay-rest.update_sip_endpoint: sdk-gap — see above.
relay-rest.delete_sip_endpoint: sdk-gap — see above.
relay-rest.list_domain_applications: sdk-gap — no SDK namespace for `/api/relay/rest/domain_applications`; domain-application assignment lives under Fabric instead.
relay-rest.create_domain_application: sdk-gap — see above.
relay-rest.retrieve_domain_application: sdk-gap — see above.
relay-rest.update_domain_application: sdk-gap — see above.
relay-rest.delete_domain_application: sdk-gap — see above.

## video — video logs have no accessor

video.list_logs: sdk-gap — `client.logs` serves messaging/voice/fax/conference logs only; there is no `client.video.logs` accessor for GET `/api/video/logs`.
video.get_log: sdk-gap — no `client.video.logs` accessor (see above).
