# ROUTE-COLLISION allowlist (python — reference)

Each entry excuses one proven, human-approved (a) route-split / (b) crud-dup
finding. Gate: `porting-sdk/scripts/route_collision.py`. Key form:
`<Class>.<canonical_op>`.

## (a) list_addresses singular-path override — the override is the SOLE live route

`CallFlows` and `ConferenceRooms` serve their addresses (and, for call_flows,
versions) under the SINGULAR sub-path — `/api/fabric/resources/call_flow/{id}/addresses`
and `/api/fabric/resources/conference_room/{id}/addresses` — while the collection
itself is the PLURAL `/api/fabric/resources/call_flows` (resp. `/conference_rooms`).
This is a real platform wire quirk, documented in the authoritative spec:

    porting-sdk/rest-apis/fabric/openapi.yaml:801  "Versions AND addresses live under
        the SINGULAR call_flow sub-path (a real platform quirk) ... Declaring
        list_addresses here overrides the FabricResource base method, which would
        otherwise use the plural collection path."
    porting-sdk/rest-apis/fabric/openapi.yaml:1074  (same for conference_room)

Python is the REFERENCE that the sibling ports (go/java/cpp) match: the generated
`CallFlows` / `ConferenceRooms` classes each declare `list_addresses` directly
(`signalwire/rest/namespaces/fabric_resources_generated.py:327` and `:477`, each
with `# type: ignore[override]`), which REPLACES the inherited
`FabricResource.list_addresses` (plural collection path). By Python method override
the base plural-path method is unreachable through a `CallFlows` / `ConferenceRooms`
instance; there is exactly ONE live route for `list_addresses` on each class — the
spec's canonical singular path (proven by the generated `*Wire` REST coverage test
journalling the singular path).

The gate still flags it because its plural-collection heuristic sees the divergent
segment; but the surface records a single `list_addresses` member and there is a
single canonical route — the correct (spec/wire) one. These are the identical,
user-approved exceptions already carried by signalwire-go, signalwire-java, and
signalwire-cpp (all APPROVED by user 2026-07-07), of which the Python reference is
the origin.

- CallFlows.list_addresses — spec-declared singular-path override (openapi.yaml:801); Python `list_addresses` override replaces the base, single live route = canonical singular path. (APPROVED: user 2026-07-07 — reference origin of the go/java/cpp entries approved 2026-07-07)
- ConferenceRooms.list_addresses — spec-declared singular-path override (openapi.yaml:1074); Python `list_addresses` override replaces the base, single live route = canonical singular path. (APPROVED: user 2026-07-07 — reference origin of the go/java/cpp entries approved 2026-07-07)
