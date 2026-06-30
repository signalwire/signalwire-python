# conversation_kit

Product-agnostic language utilities for voice agents — the deterministic
pieces an agent needs to *understand what the caller said*, *compute the right value*, and
*say things back correctly*, without baking in any one product's wording.

```
caller speech ──▶ understand (dates, inputs) ──▶ compute ──▶ speak back (verbalizer) ──▶ TTS
```

It ships with the SignalWire SDK; an agent calls these helpers and wraps the results into
its SWAIG responses and prompts.

## Why it exists

Models are excellent at understanding intent and unreliable at two things that must be
exact on a live call:

1. **Calendar math** — "next Saturday" must resolve to one specific date, every time.
2. **Speaking values aloud** — "0.156 mm/s", "a.b@gmail.com", or "2026-07-04" must come out
   as natural, correct speech in the caller's language, not as digits a TTS engine mangles.

`conversation_kit` does both deterministically, so the model never has to.

## The three layers

```python
from signalwire.conversation_kit import compute_date, validate_input, verbalizer
```

### `dates` — spoken-date math

The model passes the *semantic parts* it heard; the arithmetic happens here, so a wrong date
can never be spoken.

```python
from datetime import date
from signalwire.conversation_kit import compute_date, RESOLVE_DATE_PARAMS, WEEKDAYS

today = date(2026, 6, 30)                                          # a Tuesday
compute_date({"weekday": "saturday", "which": "next"}, today)      # -> date(2026, 7, 11)
compute_date({"relative": "tomorrow"}, today)                      # -> date(2026, 7, 1)
compute_date({"day": 15, "month": 7}, today)                       # -> date(2026, 7, 15)
```

`next <weekday>` = that weekday in the following calendar week; a bare/"this"/"coming" weekday
= the soonest upcoming one (a same-day weekday rolls forward, so the agent never silently books
"today"). Returns `None` when nothing resolvable was supplied. `RESOLVE_DATE_PARAMS` is a
ready-made JSON-schema fragment for a `resolve_date` tool's parameters; `WEEKDAYS` is the
canonical lowercase list.

### `inputs` — validation + typed-input channel

```python
from signalwire.conversation_kit import validate_input, input_request_payload

validate_input("a.b@gmail.com", "email")    # True  (also "phone", "number")
input_request_payload("installer_email", label="Installer's email", input_type="email")
# -> {"type": "input_request", "field": "installer_email",
#     "label": "Installer's email", "input_type": "email"}
```

`input_request_payload(...)` is the small event an agent sends to a connected app to reveal +
focus an on-screen field (for values speech-to-text can't reliably capture); `validate_input`
checks the typed value before it's accepted.

### `verbalizer` — TTS-ready, per-language output

```python
from signalwire.conversation_kit import verbalizer

v = verbalizer.get("pl")
v.number("2.6")              # 'dwa przecinek sześć'
v.unit("0.156", "mm/s")      # 'zero przecinek sto pięćdziesiąt sześć milimetra na sekundę'
v.date("2026-07-04")         # 'sobota, czwartego lipca dwa tysiące dwudziestego szóstego roku'
v.email("a.b@gmail.com")     # 'a kropka b małpka gmail kropka com'
verbalizer.available()       # ['en', 'pl']
```

Two helpers the agent leans on most:

- **`measure_text(text)`** rewrites measured values + units found in a model-produced sentence
  into spoken form (idempotent, safe to run over any reply).
- **`guidance(glossary=None)`** returns per-language speaking rules woven with an optional
  product glossary, ready to drop into the model's prompt.

`get(lang)` falls back to English for an unregistered language, so callers never guard.

## Adding a language

`Verbalizer` is a concrete, language-neutral base — subclass it and override only what differs
(`number`, `date`, usually `unit`/`spell`, plus the `SEPARATORS`/`LETTERS`/`MEASURE_UNITS`/
`INSTRUCTION` class attributes; `email`/`measure_text` are driven by those attributes). Because
the base is a safe fallback, a partial plugin still works.

```python
from typing import ClassVar
from signalwire.conversation_kit.verbalizer import Verbalizer, register

class GermanVerbalizer(Verbalizer):
    lang: ClassVar[str] = "de"
    def number(self, value): ...
    def date(self, iso): ...

register(GermanVerbalizer())     # get("de") now resolves to it
```

Built-in languages (EN, PL) register in `verbalizer/languages/`; an application can register
its own at runtime with `register(...)` without modifying the SDK. A language is only fully
"supported" when three things line up: a verbalizer plugin, inclusion in the agent's multilingual
`allowed` set, and a TTS voice.

## Design principles

- **Deterministic, not generative** — same input, same output; the model decides *what*, this
  decides the exact value and wording.
- **Zero dependencies** — lightweight, trivially unit-testable.
- **Product-agnostic** — no product names, no business logic, no I/O; the agent supplies the
  product wording and wraps these outputs into its own responses.
- **Plugin languages** — output is per-language behind one interface; new languages are additive.
