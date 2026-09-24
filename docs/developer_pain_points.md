# Developer pain points

This guide starts from problems developers recognize when they build voice agents. Each entry names the symptom, the mechanism that addresses it, and the responsibility that still belongs to the application. It's a map of capabilities, not a claim that every safeguard is enabled automatically.

It was checked against the `signalwire-sdk` source at commit `63aed86`: version 3.4.3 in `pyproject.toml`, plus the changes listed under Unreleased in `CHANGELOG.md`. It describes the SDK's contract. It doesn't verify the platform's server-side behavior, and no live call was tested. The [PGI implementation guide](pgi_agent_guide.md) labels its capabilities with these entries' `Pxx` numbers. Source identifiers such as [S03] resolve in [Sources](#sources).

A working voice demo is not the same as a dependable application. The difficult work often lives around the model: reaching users, managing live media, preserving state, enforcing prerequisites, executing real actions, and recovering when something fails.

SignalWire combines the communications runtime with an agent programming model. You define behavior and business logic. The platform runs the voice/AI interaction and applies the workflow and call instructions you provide. The model interprets and explains; your software authorizes and executes. [S01, S02]

## Start here

Pick the entries that match where you are:

- Building your first voice agent: P01-P06.
- Making a demo dependable: P07-P18 and P25-P30.
- Embedding an agent in a product: P19-P24 and P31-P36.

## Why this is more than tool calling

A conventional tool integration answers: **What happens when the model asks for this function?**

[Programmatically Governed Inference](programmatically_governed_inference.md) (PGI), also called System-Directed AI, also answers: **Which functions, facts, instructions, and transitions should the model even have available at this moment?**

That distinction changes where reliability comes from. You do not tell the model the entire business process and ask it not to break the rules. You construct a focused task, expose its permitted operations, and let trusted code advance the interaction when the real conditions are satisfied. [PGI, S03-S05]

### Three responsibilities, not one giant prompt

The work splits between three owners:

**The model:** understand what a person means, collect information, request an available tool, and explain an outcome.

**Your application:** authenticate users, enforce business rules, validate requests, consult systems of record, commit transactions, and decide consequential outcomes.

**The platform:** run the communications and AI session, apply tool and transition scoping, manage context visibility, execute native interaction actions, and expose control and lifecycle events. [S01-S08]

The application can be deeply programmable without owning every audio packet. A webhook can carry business logic without turning the application into the media runtime.

### Three kinds of support

Each entry falls into one or more of these:

**Handled by the platform:** the native media/AI session and its communications operations.

**Controlled through SDK primitives:** tool visibility, legal model navigation, context/history projection, structured results, and workflow actions.

**Implemented in your backend:** authorization, transaction correctness, durable state, idempotency, and business policy. PGI gives these controls a place in the interaction; it does not replace them.

### A precise limit

Taking away the model's authority to charge a wrong amount is different from guaranteeing it can never say a wrong amount. PGI addresses consequential authority and reduces unnecessary model exposure. Generated speech and summaries still need appropriate validation, grounding, and testing. [PGI]

## 01. Reach users without building a media platform

### P01: I wanted an agent, and ended up building an audio pipeline

Connecting recognition, a model, speech synthesis, buffering, and call media can become a separate engineering project before the application does anything useful.

**How SignalWire addresses it:** SignalWire runs the voice and AI pipeline. Your Python service supplies agent instructions and tools; it does not have to relay each audio chunk. Start with `AgentBase`, not a custom audio bridge.

**You still own:** Your application logic, backend integrations, hosting, and end-to-end experience tests.

Sources: [S01], [S02].

### P02: The browser demo does not fit our real calling environment

A useful agent needs to work in an app, on ordinary phone calls, and with existing business telephony, without a separate behavioral implementation for each.

**How SignalWire addresses it:** The platform exposes agents through PSTN calling, SIP, and WebRTC. Keep the agent behavior reusable while choosing the appropriate phone routing, SIP integration, or browser/client connection.

**You still own:** Endpoint provisioning, access policies, caller identity, and testing each supported client path. One agent definition does not mean zero endpoint setup.

Sources: [S01], [S08].

### P03: Every conversation needs my own long-running audio worker

An application that owns the media loop must keep that worker alive and scale it with concurrent conversations.

**How SignalWire addresses it:** With the native agent path, SignalWire owns the ongoing media/AI session. Your service handles configuration and tool requests. The SDK supports conventional web services and cloud-function adapters.

**You still own:** Tool latency, webhook availability, provider limits, cold starts, and deployment configuration. RELAY applications still need an appropriate persistent connection.

Sources: [S01], [S16].

## 02. Make the conversation work in real time

### P04: The agent talks over people or keeps playing a canceled answer

Turn-taking is more than generating a fast answer. It involves speech detection, output playback, interruption, and the state of the live call.

**How SignalWire addresses it:** SignalWire handles these concerns in its voice runtime, rather than requiring an application to coordinate every media event. AI parameters and runtime actions expose tuning where the application needs it.

**You still own:** Test interruptions, silence, noise, and actual playback on target endpoints. Integrated handling is not a promise of zero latency or flawless recognition.

Sources: [S01], [S07], [S08].

### P05: A slow tool leaves the caller in silence or an endless hold

Lookups and human availability checks can take longer than a normal conversational turn. An unplanned wait sounds broken.

**How SignalWire addresses it:** Configure tool fillers for short waits. Use explicit hold/unhold controls for longer ones, with separate resume and timeout destinations. A hold can announce itself before speech detection pauses.

**You still own:** Bounded backend timeouts, a useful fallback, and a real completion signal. A hold is not background-job infrastructure.

Sources: [S04], [S05], [S08].

### P06: Names, jargon, languages, and pronunciation need endless prompt patches

A correct workflow still fails when the agent misunderstands a product name or speaks it poorly.

**How SignalWire addresses it:** Configure languages and voices, recognition hints and pattern hints, pronunciation rules, and appropriate turn parameters. These controls sit beside the workflow rather than being buried in a single prompt.

**You still own:** Verify supported voice/model settings and test with realistic speakers and audio. Hints improve recognition; they do not establish facts or identity.

Sources: [S07].

## 03. Keep consequential decisions in software

### P07: The model uses a tool that does not belong at this stage

Giving the model every available tool makes it responsible for remembering which ones are appropriate now.

**How SignalWire addresses it:** Expose a small, explicit tool set per step. A verification stage can expose only verification-related operations; a later stage can expose fulfillment. Tools are registered once and selectively made available.

**You still own:** Explicit tool lists, including empty ones, and backend authorization. An omitted list can inherit the previous active set; it is not the same as disabling tools.

Sources: [S03], [S05].

### P08: The agent skips a required step because the user asks nicely

A prompt saying "verify first" leaves workflow sequencing dependent on model compliance.

**How SignalWire addresses it:** Define permitted model transitions with contexts and steps. Where a prerequisite is mandatory, remove model navigation and let a validated tool result move the workflow. Trusted code retains transition authority.

**You still own:** Encode and test the prerequisite in software. Completion criteria describe intent; they are not proof of verification or consent.

Sources: [S03], [S04].

### P09: The agent invents a price, promise, or transaction outcome

Fluent language is not an inventory check, an authorization decision, or a completed transaction.

**How SignalWire addresses it:** Handlers consult authoritative systems and perform permitted actions. Return verified outcomes for the model to explain, while state changes and routing go to the platform separately.

**You still own:** Correct business rules and data. The model can still say something wrong; PGI limits its authority over outcomes rather than guaranteeing every utterance.

Sources: [S04], [S05].

## 04. Replace sprawling prompts with focused workflows

### P10: One giant prompt is trying to run every department and exception

As scope grows, unrelated instructions, tools, and responsibilities compete in the same model context.

**How SignalWire addresses it:** Use a shared base prompt for stable behavior, contexts for distinct modes, and steps for the current task. Change the role and available capabilities without building a separate media application.

**You still own:** Design sensible boundaries. Keep each stage focused; do not reproduce the entire workflow in every step prompt.

Sources: [S03], [S07].

### P11: The agent skips form questions or infers answers it should ask for

Collecting structured information through a freeform conversation can produce missing, reordered, or assumed values.

**How SignalWire addresses it:** Gather mode presents questions incrementally with typed submissions, optional confirmation, per-question tools, and optional isolation from sibling answers. Results accumulate as structured session data.

**You still own:** Domain validation and downstream acceptance checks. During gather, required helpers and escalation tools must be explicitly available for each question.

Sources: [S03], [S20].

### P12: Earlier instructions or answers keep contaminating the next task

Keeping everything in the model context can preserve irrelevant instructions; discarding everything can make the caller repeat useful information.

**How SignalWire addresses it:** Choose history visibility per step or context. Keep dialogue while dropping old instructions, hide prior dialogue, or reintroduce a curated summary using step history. The call log remains separate.

**You still own:** Decide what the next stage needs. Context isolation is not log deletion or a retention policy.

Sources: [S03].

## 05. Separate application truth from conversational context

### P13: The conversation transcript has become our database

Facts extracted from an informal conversation are a poor substitute for structured application state.

**How SignalWire addresses it:** Use `global_data` for session-scoped workflow data and references. Handlers can read it and return explicit updates, while durable records remain in your database or system of record.

**You still own:** Cross-session persistence, validation, concurrency, and transactions. Do not store caller-specific truth in a shared Python agent object.

Sources: [S04], [S07], [S26].

### P14: We put whole customer records into the prompt just in case

Overexposing data increases the amount the model can misuse or repeat, even when most fields are irrelevant.

**How SignalWire addresses it:** Keep authoritative data behind tools and project only the facts needed for the current task. Structured session data is not automatically the full model context; explicitly surfaced fields cross that boundary.

**You still own:** Minimize sensitive values in prompts, tool results, logs, and summaries. Prefer opaque references to secrets. This is not automatic redaction or compliance certification.

Sources: [S03], [S04], [S07].

### P15: The agent guesses when it should consult a knowledge source

Adding documents to a giant prompt does not make live facts current or ensure a useful answer is grounded.

**How SignalWire addresses it:** Use search skills, local search indexes, DataSphere, or application tools to retrieve relevant material on demand. Scope retrieval to the current task and return concise, attributable facts.

**You still own:** Freshness, access controls, source quality, and a clear no-answer path. Retrieval is evidence, not authorization, and retrieved text remains untrusted input.

Sources: [S10], [S11].

## 06. Make tools operate the application, not only talk about it

### P16: The tool returns text, then we hope the model does the next thing

"Tell the user it worked" should not also be the mechanism that commits state, updates a screen, or changes call routing.

**How SignalWire addresses it:** `FunctionResult` separates model-facing outcomes and instructions from platform actions. A handler can return a data update, step change, client event, or call operation alongside the explanation.

**You still own:** External transaction correctness and failure recovery. One structured result does not make unrelated external services one rollback-capable transaction.

Sources: [S04], [S26].

### P17: A small API lookup requires another custom webhook service

Writing and operating a proxy for every small REST integration adds glue code without adding business value.

**How SignalWire addresses it:** `DataMap` defines server-executed API calls, response mapping, expressions, and fallback results. Use it for a direct REST integration; use Python handlers for substantial policy and transaction logic.

**You still own:** API credentials, fixed/allowed destinations, authorization at the upstream service, and useful error handling. DataMap is not arbitrary Python execution.

Sources: [S09].

### P18: Every agent rebuilds the same tools and integrations

Copying search, date/time, or integration code across agents makes maintenance and behavior inconsistent.

**How SignalWire addresses it:** Package capabilities as skills, import selected remote functions, or integrate MCP tools. Compose reusable implementation while still choosing which tools each phase exposes.

**You still own:** Review imported tools, configuration, credentials, and trust boundaries. Loading an integration does not mean every imported operation should be visible everywhere.

Sources: [S10], [S19], [S07].

## 07. Treat AI, people, and interfaces as one interaction

### P19: "Agent handoff" hides several different behaviors

Changing a role, consulting a specialist, temporarily connecting elsewhere, and permanently transferring the call have different state and lifecycle needs.

**How SignalWire addresses it:** Use context changes for a new role in the same agent; tools for a bounded consultation; temporary connect/transfer for return behavior; and final transfer for a true handoff.

**You still own:** Choose the right pattern, define return/failure behavior, and decide which state crosses the boundary. Hosting two agents does not orchestrate them.

Sources: [S03], [S04], [S22].

### P20: Escalation to a human loses context or is only a spoken promise

An agent saying "I will transfer you" is not the same as routing the live call with a useful handoff.

**How SignalWire addresses it:** A handler can execute native call actions, announce the transfer first, and send the receiving application selected context through the integration you define.

**You still own:** Destination availability, queue policy, access to the handoff record, and no-answer handling. A raw phone or SIP destination does not automatically receive structured state.

Sources: [S04], [S08].

### P21: The voice says one thing while the application screen shows another

Parsing spoken language to drive the interface couples application behavior to model wording.

**How SignalWire addresses it:** Return structured client events and runtime state changes from the same handler that produced the result. Let the UI react to application data, not to a guessed interpretation of speech.

**You still own:** Client subscriptions, event correlation, reconnect recovery, and a durable source for resynchronizing the UI. Events are not durable storage.

Sources: [S04].

## 08. Embed the experience without leaking authority

### P22: Switching between text and voice starts the conversation over

A new medium can begin before the old one has finished saving, creating missing context and race conditions.

**How SignalWire addresses it:** The SDK includes `AIChatClient`, `ChatGateway`, and `HandoffRouter`. The handoff mechanism supports nonce-bound call access and waiting for application-confirmed capture before moving to the replacement leg.

**You still own:** Persist and restore the appropriate record through callbacks. Configure capture ordering and shared/sticky state where required; continuity is not automatic cross-channel memory.

Sources: [S13], [S14], [S22].

### P23: Embedding a chat widget exposes our project API token

A browser cannot safely hold broad server credentials to start an agent conversation.

**How SignalWire addresses it:** `ChatGateway` keeps project credentials server-side, binds a publishable key to a selected agent configuration, issues signed handles, and applies conversation/turn caps.

**You still own:** Abuse prevention, stable signing secrets, and distributed limiting. A publishable key is public; origin restrictions are not user authentication. Voice-client authorization is configured separately.

Sources: [S13].

### P24: Personalization leaks between customers or tenants

Mutating a shared agent instance can accidentally carry one caller's configuration into another caller's session.

**How SignalWire addresses it:** Per-call callbacks configure an ephemeral agent copy. Use them to vary prompts, languages, tools, and session data. Composable callbacks avoid silently replacing an earlier configuration function.

**You still own:** Authenticate tenant selection and namespace durable state. Never grant privileges from a caller-supplied tier or mutate shared per-caller state.

Sources: [S06].

## 09. Design for failure rather than only the happy path

### P25: A retry creates the same booking, case, or message twice

Tools and networks fail in ways that leave the caller unsure whether an operation completed.

**How SignalWire addresses it:** Because handlers own execution, place idempotency keys, transaction checks, and authoritative status lookup in normal backend code. Return the existing outcome on a safe retry and move the workflow accordingly.

**You still own:** The idempotency implementation. PGI enables this design; it does not automatically make every external side effect exactly once.

Sources: [S04], [S05].

### P26: Anyone with a callback URL can try to invoke a privileged tool

A hidden tool is not a replacement for authenticated HTTP endpoints and application authorization.

**How SignalWire addresses it:** The SDK supports Basic Auth, function tokens, and inbound webhook signature validation. Configure the relevant mechanisms, then validate identity, tenant, state, and permissions in handlers. With a signing key set, the agent refuses any POST without a valid SignalWire signature, on a web server or a serverless platform. A `secure=True` tool runs only with the token minted for that function and call. Releases up to 3.4.3 don't enforce these checks on every path; the Unreleased section of `CHANGELOG.md` lists the fixes.

**You still own:** Enable signature checking, protect proxy trust, manage secrets, and reject unauthorized business operations. Caller ID alone is not verified customer identity.

Sources: [S12], [S27].

### P27: A rolling deployment suddenly breaks tools on active calls

Tokens signed with a random process-local secret may fail after a restart or on another replica.

**How SignalWire addresses it:** Set a stable SWAIG signing secret across the replicas serving an agent. Keep inbound webhook signing configuration distinct. Chat handles and handoff registries also have explicit multi-replica requirements.

**You still own:** Secret storage and rotation, shared state or routing strategy, and deploy-while-active tests. Reconnection alone does not guarantee session recovery.

Sources: [S12], [S13], [S14].

## 10. Test and observe behavior as software

### P28: We can only test the agent by calling it and hoping

Listening to a demo does not verify legal transitions, tool exposure, or backend invariants.

**How SignalWire addresses it:** Use `swaig-test` to inspect SWML, discover tools, and execute handlers locally. Add unit tests for business rules and serialized workflow contracts, then use live tests for speech and platform behavior.

**You still own:** Adversarial scenarios, realistic calls, regression coverage, and deployment checks. Local handler tests do not exercise runtime tool scoping or audio behavior.

Sources: [S15], [S03], [S04].

### P29: When something goes wrong, we only have the final transcript

The final words do not explain which step, tool, or application action produced an outcome.

**How SignalWire addresses it:** Use debug events, call logs, step/transition information where provided, RELAY control IDs, and application logs. Correlate model requests with handler decisions and platform actions.

**You still own:** Retention, redaction, correlation IDs, and alerting. Do not log full raw payloads or assume every diagnostic is enabled by default.

Sources: [S02], [S24], [S26].

### P30: Post-call summaries become the only record of what happened

A generated recap can be useful and still be wrong about whether an action completed.

**How SignalWire addresses it:** Keep authoritative outcomes in your application. Use call-end hooks for transcript capture and post-prompt callbacks for generated summaries. The SDK distinguishes these lifecycle paths.

**You still own:** Durable, idempotent persistence and schema validation of summaries. Do not let an inferred summary become the source of transaction truth.

Sources: [S02], [S26].

## 11. Keep the programming model composable

### P31: We need both declarative agents and live application control

Some tasks are best described as a flow; others require reacting immediately to application events.

**How SignalWire addresses it:** Use `AgentBase` and SWML for behavior, RELAY for persistent event-driven call control, and REST for resources or appropriate HTTP call commands. AI is already an operation on a live `Call` object.

**You still own:** Choose the surface to match the task. Not every action has identical semantics across interfaces, and an AI action's lifetime is not the whole call's lifetime.

Sources: [S01], [S08], [S17].

### P32: The AI agent cannot fit into our existing call flow

Applications often need an announcement, recording, menu, verification flow, or routing decision before or after an AI interaction.

**How SignalWire addresses it:** Add pre-answer, post-answer, and post-AI operations around the AI verb in the same SWML document. Use `SWMLService` for non-AI flows and explicit platform actions during a conversation.

**You still own:** Lifecycle ordering and exit paths. A final transfer or hangup may bypass later operations; do not confuse ending step mode with ending the call.

Sources: [S02], [S03], [S21].

### P33: Adding agents means multiplying servers and duplicated endpoints

A product may need several specialists, reusable application routes, and different entry points without a separate deployment for each.

**How SignalWire addresses it:** `AgentServer` hosts multiple agents by route. `AgentBase` can be embedded in a web application, while `SWMLService` serves other flows. SIP username routing provides another entry-point mapping.

**You still own:** Route ownership, authentication, per-agent configuration, and resource isolation. Shared hosting is an operational choice, not automatic cross-agent memory.

Sources: [S01], [S02], [S06], [S25].

## 12. Retain control as the product grows

### P34: Migrating frameworks means rewriting the whole agent at once

A team may already have familiar agent APIs and tools but want the communications runtime elsewhere.

**How SignalWire addresses it:** LiveWire offers a documented LiveKit-style compatibility surface. Use it where its mapped behavior fits, or use the native SDK for explicit PGI controls and full clarity.

**You still own:** Review the compatibility table: several STT/TTS/VAD/plugin controls are stubs or no-ops because the platform owns them. It is not a complete drop-in replacement.

Sources: [S18].

### P35: Changing a model means rebuilding the application architecture

When business rules depend on one model's obedience, every model change can affect more than language quality.

**How SignalWire addresses it:** Keep business policy in handlers and model-visible scope in the workflow. Configure supported model, voice, and language choices within the platform rather than rebuilding the media pipeline.

**You still own:** Verify supported options and retest tool use, language quality, latency, and cost. PGI reduces dependence on model compliance; it does not make models behaviorally identical.

Sources: [S07].

### P36: The agent is a silo that cannot use the rest of communications

Real applications may need messages, recording, conferencing, SIP operations, media taps, or another call, not only a spoken answer.

**How SignalWire addresses it:** Function results and the broader SDK expose native communications actions alongside AI behavior. Use those primitives directly instead of making the model narrate an action your software never performs.

**You still own:** Permissions, destination allowlists, user consent, applicable policies, and validation of each action. Expose only the operations needed for the current task.

Sources: [S04], [S08], [S17].

## One example: a service request, from conversation to completed work

A caller asks for an equipment repair. The model can understand that request without being trusted to create any repair, for any customer, at any time. The request moves through these phases:

| Phase | What the model gets | What software does |
|---|---|---|
| Identify | The minimum questions and identity-related tools | Establish the authenticated customer and permitted account scope |
| Collect | One focused task or gather sequence | Validate and retain the necessary fields |
| Prepare | Only request-preparation tools | Check eligibility, construct the proposed action, and return a factual preview |
| Review | Tools for revision, confirmation intent, or escalation | Enforce the appropriate approval policy against the current proposal |
| Execute | No authority to invent the result | Commit idempotently, then return outcome data and platform actions |
| Continue or hand off | The information relevant to the next task | Change the step, update the UI, connect a person, or end the call |

A user saying "skip verification" does not create a verification result. A model saying "done" does not create a completed transaction. A repeated tool request does not have to create a second case. Those are software properties, tested independently of the voice interface. [S03-S05]

For low-risk operations, the model may interpret a spoken confirmation. Where stronger evidence is required, collect it through a trusted application interaction or dedicated input flow, and bind it to the exact action being approved. A tool named confirm is not proof of consent.

The [reference implementation in the PGI implementation guide](pgi_agent_guide.md#6-reference-implementation) builds the prepare, review and execute phases of a flow like this one, with tests.

### What the developer builds

An agent definition, small focused handlers, explicit workflow boundaries, backend persistence, and integration with the surrounding product. Not a recognition/model/synthesis relay loop. The live experience is still tested on real endpoints. [S01-S05]

## An adoption path that does not start with a rewrite

Take these steps in order:

**Start with one useful task.** Define a business outcome and the invariants that must remain true even when the model misunderstands a user.

**Choose the right surface.** Use `AgentBase` for native agents, `SWMLService` for declarative non-AI flows, RELAY for event-driven live control, and REST for resource management and supported call commands. These are complementary choices. [S01, S08, S17, S21]

**Add only the necessary boundaries.** An informational agent does not need a twenty-stage workflow. A transaction flow does need explicit prerequisites, restricted capabilities, and backend checks. Add strictness where it protects an invariant.

**Test software first, conversation second.** Verify handlers and emitted workflow configuration locally. Then test calls, interruptions, tool failures, transfers, authentication, and rolling deployments. [S15]

**Expand by composition.** Add another task, language, agent route, tool, or communication path without moving policy into prompts or rebuilding the media loop. [S01-S08]

## Glossary

These terms appear throughout the entries:

| Term | Plain meaning |
|---|---|
| AgentBase | The Python foundation for defining an agent's behavior and tools |
| SWML | SignalWire Markup Language: the platform's declarative instructions for an interaction |
| SWAIG | SignalWire AI Gateway: tool definitions, requests, results, and platform actions |
| PGI / System-Directed AI | A programming discipline that keeps consequential authority in software and deliberately scopes the model's operating environment. See [Programmatically Governed Inference](programmatically_governed_inference.md). |
| AI Kernel | The platform's integrated AI/interaction runtime; not a claim that every model runs inside the Python service |
| Context / step | A conversation mode and its current phase |
| global_data | Structured session data, separate from the model's automatically visible context |
| FunctionResult | A handler result that can address both the model and the platform |
| DataMap | A server-executed tool mapping, often for a direct REST integration |
| RELAY | Persistent, event-driven application control of calls and messaging |
| PSTN / SIP / WebRTC | Ordinary telephone access, business/Internet telephony, and real-time client/browser communications |

## Sources

The identifiers in the entries resolve to these documents and source files in this repository. They use the same numbers as the [PGI implementation guide's sources](pgi_agent_guide.md#122-implementation-sources).

- [PGI] [Programmatically Governed Inference](programmatically_governed_inference.md) - `docs/programmatically_governed_inference.md`.

- [S01] [SDK architecture and package surfaces](../README.md) - `README.md`.

- [S02] [Agent construction and call lifecycle](../signalwire/signalwire/core/agent_base.py) - `signalwire/signalwire/core/agent_base.py`.

- [S03] [Contexts, steps, history, and gather implementation](../signalwire/signalwire/core/contexts.py) - `signalwire/signalwire/core/contexts.py`.

- [S04] [Tool results and native platform actions](../signalwire/signalwire/core/function_result.py) - `signalwire/signalwire/core/function_result.py`.

- [S05] [Tool registration, dispatch, and schemas](../signalwire/signalwire/core/mixins/tool_mixin.py) - `signalwire/signalwire/core/mixins/tool_mixin.py`.

- [S06] [Per-request configuration and embedded web service](../signalwire/signalwire/core/mixins/web_mixin.py) - `signalwire/signalwire/core/mixins/web_mixin.py`.

- [S07] [AI configuration, languages, state, and model parameters](../signalwire/signalwire/core/mixins/ai_config_mixin.py) - `signalwire/signalwire/core/mixins/ai_config_mixin.py`.

- [S08] [RELAY live call implementation](../signalwire/signalwire/relay/call.py) - `signalwire/signalwire/relay/call.py`.

- [S09] [DataMap server-executed tools](datamap_guide.md) - `docs/datamap_guide.md`.

- [S10] [Skills and reusable integrations](skills_system.md) - `docs/skills_system.md`.

- [S11] [Search and knowledge integration](search_integration.md) - `docs/search_integration.md`.

- [S12] [Authentication, signatures, and signing secrets](security.md) - `docs/security.md`.

- [S13] [Browser AI Chat Gateway](ai_chat_gateway.md) - `docs/ai_chat_gateway.md`.

- [S14] [Voice/text continuity and secure handoff routing](../signalwire/signalwire/ai_chat/handoff.py) - `signalwire/signalwire/ai_chat/handoff.py`.

- [S15] [Local CLI testing](cli_guide.md) - `docs/cli_guide.md`.

- [S16] [Serverless deployment adapters](cloud_functions_guide.md) - `docs/cloud_functions_guide.md`.

- [S17] [REST resource management and call control](../rest/README.md) - `rest/README.md`.

- [S18] [LiveWire compatibility scope](../livewire/README.md) - `livewire/README.md`.

- [S19] [MCP gateway and tool integration](mcp_gateway_reference.md) - `docs/mcp_gateway_reference.md`.

- [S20] [Gather per-question capability scoping](../examples/gather_per_question_functions_demo.py) - `examples/gather_per_question_functions_demo.py`.

- [S21] [Declarative SWML without an AI agent](swml_service_guide.md) - `docs/swml_service_guide.md`.

- [S22] [AI Chat client implementation](../signalwire/signalwire/ai_chat/client.py) - `signalwire/signalwire/ai_chat/client.py`.

- [S24] [RELAY event and action model](../relay/docs/events.md) - `relay/docs/events.md`.

- [S25] [Agent hosting and shared HTTP server](../signalwire/signalwire/agent_server.py) - `signalwire/signalwire/agent_server.py`.

- [S26] [SWAIG request/result contract](swaig_reference.md) - `docs/swaig_reference.md`.

- [S27] [Release notes, including the Unreleased changes](../CHANGELOG.md) - `CHANGELOG.md`.
