# One SDK, Every Platform

## The Problem

We have a Relay adoption problem. Developers who build on SignalWire overwhelmingly choose webhooks. They write SWML, point a URL at us, and move on. Relay is more powerful, but almost nobody uses it. And we know why.

A developer who starts with webhooks and outgrows them faces a rewrite. Different SDK. Different programming model. Different concepts. The code they wrote doesn't transfer. So they don't switch. They work around Relay's absence with increasingly complex webhook architectures instead of adopting the tool that was designed for their use case.

Meanwhile, we maintain separate SDKs per platform, each with its own conventions. The Browser SDK uses RxJS observables. The existing Node Relay SDK has its own patterns. A Python developer looking at both would struggle to see they come from the same company. This means every new platform is built from scratch, every new feature is implemented independently, and every developer who touches more than one platform starts over.

## The Direction

Build a new generation of SignalWire SDKs that share a design language across every platform while using native idioms on each. Make transport - WebSocket or webhook - a configuration choice, not a different SDK.

A developer who learns SignalWire on Node.js should recognize SignalWire on Python. A developer who starts with webhooks should be able to move to WebSocket by changing a config value, not rewriting their application.

## What We Mean by Design Language

Think about how Apple designs products. A MacBook and an iPhone don't work the same way. macOS has keyboard shortcuts and a menu bar. iOS has touch gestures and a tab bar. But you'd never mistake either one for someone else's product. The hardware materials, the typography, the interaction principles, the way settings are organized - these create a family resemblance that doesn't require the products to be identical.

SignalWire SDKs should work the same way. Regardless of platform, a developer should encounter the same entry point (`SignalWire`), the same namespacing (`client.voice`), the same entity names (`Call`, `Recording`, `Listener`), the same action names (`dial`, `answer`, `play`, `record`, `ai`), and the same parameter shapes. That's the design language.

What changes per platform is the execution model. Node.js uses EventEmitter and async/await because that's what Node.js developers expect. The browser uses RxJS observables because that's the reactive pattern the browser SDK already established. Python uses decorators and context managers. Swift uses AsyncSequence.

Here's what the same IVR looks like across four platforms:

**Node.js**
```javascript
listener.on('call', async (call) => {
  await call.answer();
  const result = await call.prompt({ digits: { max: 1 } });
  if (result.digits === '1') {
    await call.connect({ to: { pstn: '+15551111111' } });
  }
});
```

**Python**
```python
@listener.on_call
async def handle_call(call):
    await call.answer()
    result = await call.prompt(digits={"max": 1})
    if result.digits == "1":
        await call.connect(to={"pstn": "+15551111111"})
```

**Browser**
```javascript
listener.calls$.subscribe(async (call) => {
  await call.answer();
  const result = await call.prompt({ digits: { max: 1 } });
  if (result.digits === '1') {
    await call.connect({ to: { pstn: '+15551111111' } });
  }
});
```

**Swift**
```swift
for await call in listener.calls {
    try await call.answer()
    let result = try await call.prompt(digits: .init(max: 1))
    if result.digits == "1" {
        try await call.connect(to: .pstn("+15551111111"))
    }
}
```

Every one of these is immediately recognizable as SignalWire. Every one of them is idiomatic for its platform. The design language transfers. The execution model doesn't need to.

## Transport as Configuration

Today, choosing between webhooks and Relay means choosing a different SDK with a different API. That's the core problem. Instead, transport should be a deployment decision, like choosing between PostgreSQL and MySQL - the application code stays the same, the infrastructure underneath changes.

```javascript
// WebSocket (Relay) - default
const client = new SignalWire({ project, token });

// Webhook (SWML) - same API, different transport
const client = new SignalWire({
  project,
  token,
  transport: 'webhook',
  webhook: { host: 'https://myapp.example.com', port: 3000 },
});
```

The handler code after this is identical for simple cases. The SDK translates your handler into the appropriate protocol - WebSocket commands for Relay, SWML documents for webhooks.

## Honest Limits

Here's where we have to make a choice, and the choice we're making is honesty over magic.

Webhooks and WebSockets are fundamentally different. A webhook is a single HTTP request/response. The server sends a request, your application returns a response, and the connection closes. A WebSocket is a persistent, bidirectional channel. Your application can send and receive messages at any time for the life of the connection.

Some things that are trivial over a WebSocket are hard or impossible over webhooks. Looking up a customer in your database before deciding how to route their call. Checking what time it is. Anything where the answer depends on something outside the SWML document. These require a persistent connection because the logic depends on state that only exists at runtime.

We could try to paper over this difference. Build a replay engine that stores state between webhook callbacks, add constraints that force developers to write deterministic code, require Redis for state sharing across load-balanced servers. We explored this path. It adds complexity to every layer of the SDK, confuses developers when it breaks, and the edge cases are brutal.

Instead, we're being direct about what works where. The SDK supports three tiers of complexity:

**Simple sequential flows** work identically in both transports. Answer a call, play a message, connect to another number. The SDK translates this to SWML or Relay commands transparently. This covers a large percentage of real-world use cases.

**Branching based on call actions** also works in both transports. Prompt for a digit, route based on the response. In webhook mode, the SDK maps this to SWML's native branching. In WebSocket mode, it's just JavaScript. The code looks the same.

**Non-deterministic logic** - database lookups, time-of-day routing, external API calls - requires WebSocket transport. The SDK will tell you this clearly when you try to use these patterns in webhook mode. Not with a cryptic error, but with a message that says what's happening and what to do about it.

## The Migration Story

This is the part that matters most for adoption. Here's what migration from webhooks to WebSocket looks like when a developer outgrows webhook mode:

1. Delete the `transport` and `webhook` config
2. There is no step two

The handler code doesn't change. The entity names don't change. The parameter shapes don't change. The developer already knows the SDK. They just remove the transport configuration and their existing code now runs over a persistent WebSocket.

This is the entire pitch for the unified design language. It's not about making webhooks and WebSockets identical - that's impossible and trying leads to bad abstractions. It's about making sure a developer who starts with the simpler transport isn't punished when they need the more powerful one. They don't have to learn a new SDK. They don't have to rewrite their application. They change a config value.

Compare this to today's world, where switching from webhooks to Relay means throwing away your application and starting over with a different library, different patterns, and different documentation.

## What We're Choosing and What We're Giving Up

**We're choosing platform-native idioms over cross-platform code sharing.** Each SDK will be implemented independently. The Node.js SDK won't share code with the Python SDK. This means more implementation work per platform. But it means each SDK feels native to its platform, which is what determines adoption. Developers don't care how elegant your internal code sharing is. They care whether the SDK feels like it belongs in their ecosystem.

**We're choosing honest constraints over clever abstractions.** We could build a replay engine that makes webhook mode handle arbitrary logic. We're choosing not to, because the failure modes are confusing and the edge cases are many. Instead, webhook mode handles the cases it can handle well, and tells you clearly when you need WebSocket. Developers appreciate tools that are upfront about their limits far more than tools that hide them.

**We're choosing easy migration over zero-code-change portability.** We could attempt to make the exact same code run identically on both transports. That would require constraining what developers can do (no `Date.now()`, no external API calls, deterministic functions only) or building complex state management into the webhook layer. Instead, we're making the API surface identical so that migration is trivial, even if it's not literally automatic for every case.

**We're choosing a branded entry point.** `new SignalWire()` instead of `new VertoClient()` or `createRelayClient()` or whatever internal protocol name we might use. This is a small thing but it matters. Stripe is `new Stripe()`. Twilio is `new Twilio()`. The entry point is the brand. Internal protocols are implementation details.

## What This Means for Existing SDKs

The Browser SDK is already in production and has established patterns. This initiative doesn't require rewriting it. The design language was partially derived from the browser SDK's existing conventions - entity names, action names, parameter shapes. The browser SDK is already part of the family.

New SDKs (Node.js server, Python, Swift) are built from scratch following the design language. As the browser SDK evolves, it can adopt more of the shared conventions where doing so doesn't break existing users.

## What Success Looks Like

Relay adoption goes up. Not because we made webhooks worse or forced people onto Relay, but because the path from webhooks to Relay stopped being a cliff. A developer who starts with webhooks because that's what they know can upgrade to Relay when they need it without learning a new SDK.

Time to build new platform SDKs goes down. Not because of shared code, but because of shared design decisions. When someone builds the Python SDK, the API design is already done. The naming, the parameter shapes, the entity relationships, the transport abstraction - all of it has been decided and documented. The work is implementation, not design.

Developer experience across the SignalWire product line feels cohesive. A developer who uses our Node.js SDK at work and our browser SDK for a side project recognizes the patterns. A developer reading our Python docs who has only used the Node.js SDK follows along without difficulty. The products feel like they come from the same company, because they do.
