# Programmatically Governed Inference

Programmatically Governed Inference (PGI), also referred to as System-Directed AI, is an architectural discipline in which all authority over state, decisions, and side effects lives in deterministic software. The AI model is used exclusively for what it is genuinely good at: understanding natural language, interpreting human intent, calling the right tools at the right time, and communicating results. The model participates in the interaction but does not control it. The software was always in charge.

This document describes the discipline. Its examples use the Python SDK. The [PGI implementation guide](pgi_agent_guide.md) turns the discipline into rules, recipes and a tested reference implementation.

## The observation

Current AI models are extraordinarily good at language. They understand loosely phrased human input, map intent onto structured actions, and render system decisions back into natural, conversational speech. They are the best interface layer ever built for bridging the gap between how humans communicate and how software operates.

They are also inconsistent, non-deterministic, and prone to confident error. They hallucinate facts, invent outcomes, drift from instructions, and make promises that no system behind them can keep. These are not bugs that will be fixed in the next model generation. They are properties of probabilistic inference itself. A system that predicts the most likely next token will sometimes predict wrong, and it will do so with the same fluency and confidence as when it predicts right.

The industry's dominant response has been to prompt harder and hope. Give the model detailed instructions. Tell it what not to do. Add retrieval-augmented generation for grounding. Add output filtering. Add human review. This methodology (prompt and pray, as it has come to be known) treats the model as the brain of the system and everything else as a safety net beneath it.

The results are predictable. During the early development of SignalWire's AI platform, experiments with AI-powered ordering systems revealed that models would occasionally decide, unprompted, that certain menu items were sold out. Not because of any inventory signal. Because the model inferred it. The system did not crash. It did not say anything offensive. It confidently lied about availability. Unless someone was watching closely, it would have gone unnoticed. This is the insidious failure mode of prompt and pray: not catastrophic breakdown, but quiet, confident fabrication that erodes trust without announcing itself.

The deeper problem surfaces as complexity increases. Show a model all the tools it might ever need (find a restaurant, book a table, order food, process payment, handle complaints) and it will inevitably misuse them. It will call the wrong tool at the wrong time, combine tools in ways no one intended, or invoke capabilities that do not belong in the current phase of the interaction. This is not a training problem. It is a surface area problem. The more authority you give the model, the more ways it can go wrong.

You could wait for models to become perfect. You could wait the way we wait for fully autonomous vehicles to navigate every road without error. That wait may be permanent, because the problem is not insufficient intelligence. It is the nature of probabilistic systems. They are approximate by design. A system that is right 99% of the time is wrong at scale, and in production, wrong at scale means real consequences for real people.

Programmatically Governed Inference starts from a different premise. Instead of giving the model authority and trying to contain the damage, PGI assumes the model should never have authority in the first place. The model is not the brain. It is not the locus of control. It is not the source of truth. It is a controlled participant inside a larger, deterministic system that was always in charge.

## The principle

The core of PGI is a single design rule: do not tell the AI anything it does not need to know.

Do not show it tools that do not belong to the current phase. Do not give it data it should not reason about. Do not explain the full system to it. Do not trust it with decisions that software can make deterministically. Reduce the model's surface area until its only responsibilities are understanding what the human said, deciding what information to collect, and calling whichever tools are currently available to advance the interaction. Everything else is software.

This produces a property that makes PGI fundamentally different from guardrails, output filtering, or any other containment strategy: the model does not know it is being governed. It does not know that other tools exist elsewhere in the system. It does not know that a state machine is managing the interaction. It does not know that its context is being curated by the platform underneath it. It sees its current world (a prompt, a set of functions, a conversation history) and operates within it. There is nothing to reason around, nothing to game, nothing to circumvent, because the model has no awareness that anything exists beyond what it can see.

This is not achieved through prompt discipline or hope. It is enforced mechanically. The platform presents the model with only what it should see at each moment. When the moment changes, the platform changes what the model sees. The model experiences each phase of the interaction as its entire reality, unaware of the phases that came before or the phases that will come after.

This is not input validation. Input validation is what any backend does: clamp a quantity, reject a bad email, enforce a range. PGI is something deeper. It is authoring what the model believes to be true. Each step constructs the model's perceptual reality from scratch: the prompt it reads, the tools it can call, the data it can reason about. Meanwhile, authoritative state travels through `global_data`, a structured session record the model doesn't see unless the application puts a value in front of it. Account references, risk flags, verification results, workflow state: all of it flows silently between tool handlers, invisible to the model, shaping what happens next without the model ever knowing it exists.

The model listens, interprets, and speaks. It does not decide, it does not own state, and it does not know the full truth of the system. It operates on a carefully curated projection of reality, sufficient for it to perform its role, insufficient for it to act outside its bounds.

Most models are trained into an actor's frame: they behave as though performing a role. That makes the developer a set designer rather than a director. Handing the model the entire play and asking it to perform every scene in one pass exceeds what it can hold. Telling it which scene it is in, giving it the props that scene requires, and letting it play the part does not. When the scene ends, the program clears the stage, sets the next one, and places the right actor. The model performs. The software decides what is on the stage.

## Why this matters now

AI is moving into production across contact centers, enterprise communications, healthcare, financial services, and customer-facing applications, through both voice and text interfaces. The stakes are no longer demo-quality. An AI agent that handles real interactions must be correct about pricing, compliant with regulations, accurate about account state, and reliable under adversarial input. It must not hallucinate policy, invent transactions, leak sensitive data, or make commitments the business cannot honor.

Prompt and pray produces diminishing returns at production scale. Each additional layer of defense reduces the failure rate but never eliminates it, because the model retains authority. It can still reason its way around instructions, misinterpret retrieved context, or generate confident errors that pass through output filters.

The deployment process converts that residual risk into lost capability. Nothing customer-facing ships without a risk review, and risk reviews demand guarantees. When the model's behavior is the only control surface, the only available guarantee is removal: fewer tools, closed questions, scripted intents, hard refusals. The models running in production are more capable than anything their deployments are permitted to do, and the gap widens with every model release. The visible result is the deployed agent that answers a bank's phone line with a menu and "I cannot help with that," stripped until it converges on an IVR with better diction. The market then draws the wrong conclusion: that AI is not ready for production. The accurate conclusion is narrower. Ungoverned AI is not approvable, and what survives approval is often not worth deploying.

The fallback costs more than the failure. Once the agent is stripped back to a recording, the work returns to a person reading answers off a screen, which is the job the IVR was built to remove. Putting people back on that task is dragging rocks up a hill with a rope. It works, and it is the wrong use of the labor.

PGI eliminates entire categories of failure outright. If the model never sees payment data, it cannot leak it. If a function is not in its schema, a request for it has nothing to run. If a transition is not offered, it cannot take it. Unauthorized actions by the model, leaks of data it never received, and state corruption through the model stop being risks to mitigate and become structural impossibilities. Correctness of every consequential action is a property of the software, not a hope about the model.

One channel remains: speech. A model with no authority over pricing cannot charge the wrong amount, but it can still say a wrong number, the way the ordering system spoke confidently about inventory it had no signal for. PGI narrows this channel rather than eliminating it. The model's knowable facts are the projections its tools hand it, authoritative results it reports rather than beliefs it generates, and the curated context leaves far less room to fabricate. The consequential surface is eliminated. The conversational surface is contained.

The strongest test of any PGI system: replace the model with a rigid, scripted menu ("press 1 for tacos, press 2 for drinks") and the system would still produce correct outcomes. The tool handlers would still validate input, enforce business rules, clamp absurd quantities, and manage state. The experience would be worse, because the natural language interface is what makes the interaction feel human. But every order would be accurate, every payment would process correctly, and every transition would follow the rules. The model makes the interaction natural. The software makes it correct. In a PGI system, those are independent properties.

That independence also lets the model change without changing the rules. Correctness lives in the handlers and the step definitions, so a team can upgrade or replace the model and the same business rules still apply. The change still needs testing, because another model can phrase answers and choose tools differently. It doesn't reopen the question of what the agent is allowed to do.

## The mechanism

PGI is enforced through four layers of constraint, each operating independently. The model must comply with all four simultaneously. Only the first layer depends on the model's cooperation. The remaining three are mechanical.

### Layer 1: Semantic guidance

The model receives a prompt that describes its role, the current phase of the interaction, and instructions for how to behave. These are conventional prompt instructions: what to say, what not to say, what tone to use, when to ask clarifying questions.

Semantic guidance is the weakest layer. It depends on the model's compliance, which is probabilistic. A well-crafted prompt improves behavior but cannot guarantee it. PGI treats this layer as guidance, not enforcement. It is the suggestion. The remaining layers are the law.

The weakness of this layer can be partially offset through strategic reinforcement. Rather than relying on a single system prompt that the model may drift from over a long conversation, critical instructions can be reinjected at key points in the context, keeping them prominent when they matter most. Step instructions work this way: the platform injects the current step's instructions as a system message on every turn. This does not make semantic guidance mechanical, but it makes it more durable than a static prompt alone.

### Layer 2: Schema scope

At each step in a conversation, the model sees only the tools that are explicitly listed for that step. Tools that belong to other steps do not exist in the model's function schema. The model cannot call them, reference them, or reason about them, because they are not presented to it. A model can still produce the name of a tool it wasn't given. The protection is that the tool isn't active in this step, so the request has nothing to run.

This is why surface area matters. A model that sees ten tools will misuse them in ways a model that sees two will not. The failure mode is not malice or stupidity. It is probability. Given enough tools, the model will eventually find a plausible reason to call the wrong one. Schema scope eliminates this by reducing the model's options to only what is appropriate right now.

In a blackjack game, the betting step exposes only `place_bet`. The model cannot deal cards, draw cards, or resolve hands during betting because those functions are not in its schema. When the tool handler transitions the conversation to the playing step, the schema changes: `place_bet` disappears and `hit`, `stand`, and `double_down` appear. The model's capabilities change not because it was told to behave differently, but because the available operations were mechanically replaced.

The steps are defined in a context. This fragment sets each step's tools and allowed transitions:

```python
ctx = agent.define_contexts().add_context("default")
# Each step also needs its instructions (set_text), and the hand_complete
# step is defined the same way; both are omitted here.

betting = ctx.add_step("betting")
betting.set_functions(["place_bet"])
betting.set_valid_steps(["playing"])

playing = ctx.add_step("playing")
playing.set_functions(["hit", "stand", "double_down"])
playing.set_valid_steps(["hand_complete"])

lost = ctx.add_step("you_lost")
lost.set_functions([])
lost.set_valid_steps([])
```

A step that doesn't list its tools inherits the previous step's set, so a governed step always sets its list, even when the list is empty.

This is the difference between telling someone not to open a door and removing the door from the building. Schema scope does not rely on the model's judgment or compliance. It alters the environment the model operates in.

### Layer 3: Transition scope

Each step in a conversation declares which steps the model may move to next. The enforcement is mechanical and lives in the schema, not in the model's judgment. On every turn, the platform rewrites the argument schema of the model's transition tool, `next_step`, so that only whitelisted step names exist as options. The model cannot request a transition to a step that is not on the list for the same reason it cannot call a tool that is not in its schema: the option is not part of its world. An empty whitelist leaves the model no step it can request.

The whitelist constrains the model, not the software. Tool handlers, which are the developer's deterministic code, retain full transition authority. They can move the conversation to any step in the current context, or to another context, as the business logic requires. This is the authority inversion applied to control flow: the model can only request movements the system pre-approved, while the software that owns the state machine moves the conversation wherever the rules dictate. In the blackjack example, `playing` whitelists only `hand_complete`, so the model can never talk its way anywhere else; the `hit` handler, on detecting a bust, moves the conversation straight to `you_lost`, because the software is the authority and the whitelist was never a constraint on it.

The model cannot skip phases, loop back to completed steps, or jump ahead, because those requests are not expressible. PGI allows this to operate at different levels of strictness. In the simplest case, the model knows it is in a named step and receives criteria for when to request the next one. In more advanced usage, the model does not know transitions are possible at all. Tool handlers change the step silently, and the model finds itself in a new context with new instructions and new tools. It did not request the change. It did not know it could.

At maximum strictness, a step has no valid transitions and no tools. Consider the `you_lost` step in the [Layer 2 example](#layer-2-schema-scope): zero functions, zero valid transitions. The game is over. A user can beg, negotiate, or attempt to social-engineer the AI into continuing. None of it works, because the mechanism for continuing does not exist: with no transition options there is nothing to request, and with no tools there is no handler left that could move the state. There is nothing for the model to comply with or resist. The interaction is structurally complete.

### Layer 4: Execution authority

This is the most important layer. When the model calls a tool, it is not issuing a command. It is making a request that is handled by ordinary software. The tool handler receives the request, accesses authoritative state, and applies business logic. It returns a structured result with two parts: a response the model uses to answer, and actions for the platform to execute.

This handler draws a card, reports the new total, and ends the hand on a bust:

```python
from signalwire import FunctionResult


def handle_hit(args, raw_data):
    game = raw_data["global_data"]["game_state"]
    card = game["deck"].pop()
    game["player_hand"].append(card)
    score = calculate_hand(game["player_hand"])

    result = FunctionResult(
        f"You drew {format_card(card)}. Your total is {score}."
    )
    result.update_global_data({"game_state": game})

    if score > 21:
        result.swml_change_step("you_lost")

    return result
```

The model does not execute actions. The platform does. The model does not update state. The tool handler does. The model does not decide what happens next. In the example above, the model has no idea it is about to be moved to the `you_lost` step. It speaks the result. The platform changes the step. The model's world changes without its participation.

The same pattern scales to business workflows. Consider a billing agent where a customer calls to dispute a charge. During the `verify_identity` step, the model knows the customer's name and has one tool: `verify_account`. It does not know the account balance, credit history, or dispute tools exist. Once identity is verified, the tool handler silently transitions to `review_charges`, expanding the model's reality to include recent transactions and a `file_dispute` tool. The model experiences this as its whole world. It has no memory of the prior step's constraints and no awareness that `global_data` is carrying account details, risk flags, and the verification result underneath.

This handler decides whether the dispute resolves automatically or goes to a specialist:

```python
def handle_dispute(args, raw_data):
    account = raw_data["global_data"]["account"]
    risk = raw_data["global_data"]["risk_flags"]
    amount = args["disputed_amount"]

    if risk["auto_resolve_eligible"] and amount < account["auto_resolve_limit"]:
        # Application code: the billing system of record reverses the charge.
        reverse_charge(account["id"], amount)
        result = FunctionResult(
            f"The charge of ${amount:.2f} has been reversed to your account."
        )
        result.swml_change_step("resolution_summary")
    else:
        result = FunctionResult(
            "I'm connecting you with a specialist who can review this in detail."
        )
        result.swml_change_step("escalation")

    return result
```

The model requested the dispute. The tool handler read the account details and risk flags from `global_data`, applied business logic the model cannot see, and silently transitioned to either an auto-resolution or an escalation step. On the auto-resolution path, the billing system committed the reversal before the model heard about it. The model does not know which path was available, what thresholds governed the decision, or that `global_data` exists at all. It speaks the result. The platform reshapes its world.

This inversion of authority is the core of PGI. In conventional systems, the model calls tools to accomplish its goals. In PGI, the model calls tools to report human intent, and the tools accomplish the system's goals. The model is an input layer, not a decision-maker.

Not all tool calls need to reach the developer's server. The platform itself can manage certain operations internally, processing step transitions, context updates, and governance decisions that are invisible to the model and handled entirely by the infrastructure. When the conversation's step changes, the platform updates the model's prompt and available tools without the developer writing explicit handlers for that transition. The step definitions are the instructions. The platform carries them out. The developer defines what should happen. The platform ensures it does.

## Data isolation

PGI extends to how data flows through the system. The model operates on a projection of reality, not the full truth. The mechanism that makes this possible is `global_data`: a structured record that travels between tool handlers and carries authoritative state. It stays out of the model's context unless the application projects a value into it.

Consider the billing agent from the previous section. When a customer calls to dispute a charge, `global_data` carries the account details, risk flags, auto-resolve thresholds, and verification result from the moment identity is verified. The model never sees any of it. During `verify_identity`, the model knows the customer's name and nothing else. During `review_charges`, the model sees recent transactions (a curated projection) but not the risk score, not the credit limit, not the internal flags that determine whether a dispute will be auto-resolved or escalated. The tool handler reads `global_data`, applies business logic, and returns only what the model should say. The model cannot promise a credit it does not know exists. It cannot negotiate a threshold it has never seen. It reports what the system tells it to report.

This pattern recurs everywhere PGI is applied. In a blackjack game, the model knows the player's chip count and visible cards. It does not know the deck composition, the dealer's hidden card, or the internal scoring calculations. In an ordering system, the model knows which items have been added. It does not know the internal pricing logic, tax calculations, or inventory state. In every case, `global_data` carries the authoritative record and the model sees only what is safe and necessary for conversational coherence.

Hidden from the model isn't the same as secret. The platform sends `global_data` with every tool request, and the call-end payload includes it. A step's text can also pull a value into the prompt with `${...}` expansion. Keep credentials out of it, and prefer references to records your backend holds. `global_data` lasts for the session, so durable truth, such as a reversed charge, belongs in your system of record.

Sensitive operations are handled entirely outside the model's awareness. When a user needs to provide payment information, a tool handler returns a payment action (`FunctionResult.pay()`). The platform collects the card details on the phone keypad and sends them to the payment connector the application configures, which processes the charge. The model does not hear the card number, does not process it, does not retain it. It receives only the outcome, such as the payment status, and reports it as fact.

All four PGI layers converge in this single flow. The model can only call the payment tool when the conversation reaches the payment step (schema scope). The tool handler hands collection to the platform's payment flow rather than taking card details itself (execution authority). The card number, CVV, and billing details never enter the model's context (data isolation). And when processing completes, the conversation transitions to a post-payment step where the payment tool is no longer available (transition scope). The user experiences a seamless interaction in the same voice. The model was never exposed to anything sensitive. Each layer contributed independently, and the result is a payment flow that keeps the model out of the sensitive path by construction.

Data isolation also enables capabilities that model-centric architectures cannot achieve. When the platform owns data flow independently of the model, it can route information to destinations the model is unaware of. In a system with a visual interface, tool handlers can send structured events directly to a connected browser or application with `swml_user_event()`. These events update an order display, reveal cards on a table, or render content that would be impractical to communicate by voice alone. The model does not trigger these updates. The model does not know they happen.

The platform coordinates voice, visual, and data channels independently, each governed separately, producing experiences that are richer than what any single channel could deliver. This is not a workaround for the model's limitations. It is a capability that exists precisely because PGI separates the model from the system's broader behavior.

## What PGI produces

The result is something that neither pure software nor pure AI could produce alone.

Pure software is rigid. An IVR or scripted chat system can process structured input, enforce business rules, and guarantee correctness. But it cannot absorb the ambiguity of human communication. It cannot handle "give me two of those tacos and a water" or "actually, make that three, and throw in some chips." It forces the human to conform to the system.

Pure AI is fluid but unreliable. A model that handles ordering can understand any phrasing, manage conversational flow, and make the interaction feel natural. But it will occasionally invent facts, miscalculate totals, or make promises the backend cannot honor. It forces the system to hope the model behaves.

PGI combines them into something new. The AI provides flexibility at the edges: absorbing ambiguity, handling variation, maintaining conversational coherence. The software provides certainty at the core: enforcing rules, maintaining accurate state, ensuring every consequential action is correct. The tension between them is not a flaw but the design.

The deployment consequence follows directly. Because risk is bounded by architecture rather than behavior, capability no longer has to be traded away to pass review. A governed agent ships with retrieval over the full knowledge base and answers open questions in free form, because the model can inform the caller but cannot act on its own inventions; acting requires the code gate. Consequential tools (payments, account changes, scheduling, transfers) become grantable, because every invocation is validated deterministically and the sensitive data involved never enters the model's context. Two claims inside that sentence stay distinct: that the agent cannot act outside its rails is an architectural guarantee, while grounded answering from the business's data improves answer quality without being a guarantee about every sentence the model utters. The net effect inverts the industry's trade. Everywhere else, safety is purchased by making the agent do less. Under PGI, the same review passes with the capability intact. The governed agent is not the restricted version of the capable agent. It is the only version of the capable agent that reaches production.

This combination creates a new class of interactive applications. Applications where a person communicates naturally and the system responds conversationally, but every action underneath is deterministic, auditable, and correct. Applications where the AI is the voice of the system, not the mind of it. Applications that feel like talking to an intelligent agent but behave like well-tested software. This class of application could not be built reliably before. The two required components, natural language understanding and deterministic execution, were never integrated with a clear, enforced boundary between them. PGI is that boundary.

## Building with PGI

PGI is not only an architectural pattern for platform engineers. It is a methodology for every developer building AI-powered applications.

The current industry narrative tells developers that AI has changed everything. That the future belongs to prompt engineers who can coax the right behavior out of a language model. That building an AI application means writing a detailed system message and iterating until the model mostly does what you want. This narrative has produced a generation of applications that are impressive in demos and unreliable in production, because prompting a model is not programming. It is negotiation.

PGI restores programming to the equation. In PGI, the developer's traditional skills (defining state machines, writing business logic, managing data, enforcing rules in code) are exactly what makes an AI application safe and useful. The model handles language. The developer handles everything else. Tool handlers are ordinary functions. State transitions are declared in configuration, not hoped for in prompts. Business rules are enforced in code, not in natural language instructions the model might ignore.

A developer building an intake system writes a gather sequence. The platform presents the model with one question at a time and a single submission tool, `gather_submit`. The tool's schema is rebuilt for each question, with that answer's type and, when the question asks for it, a required confirmation. The model does not know how many questions remain or what the full form looks like. When an answer arrives, the platform stores it in `global_data` and silently advances to the next question. When the sequence is complete, the accumulated structured data is handed off to the next phase of the workflow. There, a handler validates the whole record before anything consequential uses it. The model never saw the form. It never had the opportunity to skip ahead, reorder questions, or submit answers to questions that were never asked.

Visibility of what came before is itself a dial the developer controls. By default, each new phase withdraws the prior phase's instructions from the model's context while the conversation itself remains visible. At stricter settings, the platform pulls the earlier dialogue out entirely, or hides the answers already collected so the model must ask rather than infer. And a hidden phase can be deliberately re-surfaced: the platform can hand the model a system-composed summary of an earlier phase instead of the raw transcript, one more curated projection standing in for the full truth. Reality authoring extends to the past, not only the present. In the SDK, these settings are the history mode of a step or context (`keep`, `default` or `hide`) and a gather's `isolated` option. A `${step_history.*}` reference in a step's text chooses what comes back. The call log keeps every message either way.

This is not the same as ordinary backend validation (clamping a quantity with `if quantity > 20: quantity = 20`, or rejecting a bad input). Those are single lines of defensive code any backend performs. The gather sequence is reality authoring: the developer constructs what the model believes to be true at each moment, and `global_data` carries the accumulated truth the model never sees.

PGI reduces the developer's working surface to business logic. The platform handles governance: managing steps, enforcing schema scope, validating transitions, isolating data, executing platform actions. The developer defines what the application should do at each phase, writes the tool handlers that implement domain logic, and lets the platform ensure the model stays within those bounds. Developers spend their time on what differentiates their application, not on trying to constrain a language model through increasingly elaborate instructions.

PGI is not all-or-nothing. A developer can start simple, with a single step and a few tools, and progressively adopt stricter patterns as their application demands it. A casual FAQ agent might use basic PGI with one step and a handful of tools. A payment flow might use maximum PGI with strict transitions, data isolation, and no-exit steps. The discipline scales with the risk profile.

This is a deliberate design choice. PGI was not conceived as a proprietary technique to be deployed internally and sold as a finished product. It was developed as a set of principles, simplified through platform design, that any developer can employ in their own applications. The tools that enforce PGI (step definitions, scoped function registries, structured tool results, platform actions, state isolation) are primitives available to every developer building on the infrastructure. The goal is not to gate a methodology behind a product. It is to give developers the means to build AI applications that work in production, using skills they already have. The foundation handles the hard problems they should not have to solve from scratch.

## What PGI is not

**PGI is not prompt and pray.** The dominant methodology in AI development treats the model as the system and the prompt as the program. Write a detailed enough system message, the thinking goes, and the model will do what you need. PGI rejects this entirely. Prompts are the weakest layer of constraint, useful for guidance but unreliable as enforcement. PGI's correctness survives the total failure of every prompt instruction, because the remaining three layers are mechanical.

**PGI is not guardrails.** Guardrails assume the model has authority and attempt to intercept the damage after the fact. They are reactive: catch bad outputs, filter harmful content, flag anomalous behavior. PGI is structural: the model never has authority in the first place. There is nothing to intercept because there is nothing to catch. The system is correct by construction, not by interception. Guardrails also pay for safety with capability, because every filter narrows what the agent may do; PGI spends architecture instead.

**PGI is not human-in-the-loop.** There is no human gating decisions in real time. The authority is software, not people. A human designed the state machine, wrote the business rules, and defined the tool handlers. But at runtime, the system operates autonomously. The governance is programmatic, built into the architecture, not applied by a human reviewing each interaction.

**PGI is not "dumb AI."** The model's capabilities are fully utilized: natural language understanding, intent recognition, conversational fluency, handling ambiguity, managing dialogue across turns. These are difficult problems that the model solves well. PGI does not diminish the model. It focuses the model on what it is good at and removes it from what it is bad at. The model is not wasted. It is deployed where it creates the most value with the least risk.

## PGI and Programmable Unified Communications

PGI is a set of design principles. Programmable Unified Communications (PUC) is the platform architecture that makes those principles mechanically enforceable.

A PUC platform owns the interaction: its state, its lifecycle, and its outcomes. When AI operates inside a PUC platform, every property of the platform applies to the AI's behavior. The AI inherits the state machine's constraints. It inherits the tool system's mediation. It inherits the data isolation model's projections. The AI does not need its own governance framework because it is governed by the same infrastructure that governs the interaction itself.

This is why PGI requires specific infrastructure to implement. A platform that separates call control from application logic (the webhook model) can approximate pieces of PGI in middleware: a step machine of its own, scoped tool lists, server-side checks. What it cannot do is bind that governance to the interaction, because the constraints and the call live in different systems. There is no step the platform itself recognizes, no state machine governing the interaction's lifecycle rather than the middleware's, and no way for a tool handler to return actions that the same system executes against the call. Every enforcement becomes a message between systems, with its own latency, its own failure modes, and no guarantee that the model's tools, the conversation state, and the call ever change together.

PGI requires the AI and the interaction platform to be the same layer. The instruction language for the AI and the instruction language for the interaction must be unified, so that a tool handler can simultaneously update the model's context, transition the conversation's step, and control the interaction's routing. This unification is what makes PGI governance mechanical rather than aspirational.

When a tool handler returns a result that says "tell the player they busted, update the chip count, and transition to the you_lost step," all three instructions arrive together. The platform that runs the call carries them out. The model speaks the result. The state updates. The step transitions. The available tools change. This happens as one coordinated response because the platform orchestrates both the AI and the interaction. On a platform where the AI is bolted onto interaction control through webhooks, these would be three separate operations with three separate failure modes, three separate race conditions, and no guarantee of consistency. One result coordinates the platform's own instructions. It doesn't make an external system, such as a billing database, part of the same transaction.

PUC provides the speed and agility to build sophisticated interactive applications rapidly. PGI provides the discipline that makes those applications safe, consistent, and trustworthy. They are complementary commitments. PUC without PGI produces applications that ship fast but behave unpredictably. PGI without PUC produces sound principles with no platform to enforce them. Together, they give developers the foundation to build applications that ship quickly and behave correctly from the first deployment.

## The broader implication

PGI rejects the idea that intelligence must be centralized inside the model. Instead, it treats intelligence as something distributed: rules and guarantees in software, language and interpretation in the model, and a clear, enforced boundary between the two.

This distribution is not a compromise. It is an optimization. Software is better at rules, state, compliance, and enforcement than any language model will be, because software is deterministic and verifiable. Language models are better at understanding human communication, managing conversational flow, and rendering structured data as natural dialogue than any scripted system will be, because models are probabilistic and adaptive. PGI assigns each component the task it is best suited for and enforces the boundary between them so that neither overreaches.

PGI is not limited to voice. The same principles apply wherever a model interacts with users: chat interfaces, multimodal applications, or any future modality. The model's role (understand the human, call the right tools, communicate the results) stays the same regardless of input modality. The platform's role (manage state, enforce constraints, execute actions, isolate data) is equally unchanged. The transport changes. The governance does not.

The economic implication is significant. Businesses navigating the AI transition face a concrete challenge: ship AI-powered products that work reliably in production, or watch competitors do it first. PGI provides a path to reliable AI without requiring every development team to solve the fundamental problems of AI governance from scratch. The principles are clear. The platform primitives that enforce them are available. Developers bring their domain expertise (the ordering logic, the compliance rules, the business workflow) and the infrastructure handles the rest.

This is not a proprietary methodology reserved for a single vendor's internal use. It is a set of principles made accessible through platform design to every developer who builds on the infrastructure. The goal has never been to centralize AI capability, to hoard a technique and sell its outputs. The goal is to distribute it: to give every development team the tools to build AI applications that are safe, consistent, and trustworthy. Developers use engineering skills they already possess, on a foundation that evolves underneath them and lifts their applications forward.

The result is a foundation for the next generation of interactive applications. Developers bring their domain expertise and engineering skills. The platform provides the governance infrastructure. The model provides the natural language interface. Each component does what it is best at, bounded by clear, enforced separations that none of them can cross. The model is never in charge, yet it is never wasted. The developer is never fighting the model, only building the system around it. And the applications that emerge are something new: conversational, adaptive, and trustworthy in systems where correctness is not optional.

## Related documentation

For more information, see these documents:

- [PGI implementation guide](pgi_agent_guide.md): rules, a capability index, recipes and a tested reference implementation for building PGI agents with this SDK
- [Developer pain points](developer_pain_points.md): the problems developers meet when building voice agents, the mechanism that addresses each, and what the application still owns
- [Contexts and Steps Guide](contexts_guide.md): steps, per-step tools, navigation, history modes and gather questions
- [FunctionResult methods reference](swaig_reference.md): tool results, platform actions, and the data each tool request carries, including `global_data`
