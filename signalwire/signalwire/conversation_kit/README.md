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
2. **Speaking values aloud** — "0.156 mm/s", "a.b@gmail.com", "2026-07-04", or "RMS" must come
   out as natural, correct speech in the caller's language, not as digits or letters a TTS
   engine mangles.

`conversation_kit` does both deterministically, so the model never has to.

## Module map

Where each thing lives — start here when extending:

| File | Responsibility | Public names |
|------|----------------|--------------|
| `__init__.py` | Package facade — re-exports the whole surface | `compute_date`, `validate_input`, `input_request_payload`, `verbalizer`, … |
| `dates.py` | Spoken-date → calendar-date math | `compute_date`, `RESOLVE_DATE_PARAMS`, `WEEKDAYS` |
| `inputs.py` | Input validation + typed-input (keypad) channel payload | `validate_input`, `is_valid_email/phone/number`, `input_request_payload`, `INPUT_REQUEST_TYPE` |
| `verbalizer/__init__.py` | Verbalizer facade — registers the built-in languages | `get`, `register`, `available`, `Verbalizer` |
| `verbalizer/base.py` | The `Verbalizer` interface **and** a safe language-neutral fallback | `Verbalizer` |
| `verbalizer/registry.py` | Language lookup with English fallback | `get`, `register`, `available` |
| `verbalizer/languages/en.py`, `pl.py` | Built-in language plugins | `EnglishVerbalizer`, `PolishVerbalizer` |

Everything imports through the package root:

```python
from signalwire.conversation_kit import compute_date, validate_input, verbalizer
```

## The three layers

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

# English — mostly passthrough: a TTS engine already reads English numbers and dates
# correctly, so the plugin only steps in where it must (e.g. spelling out an email's
# separators). This is why the outputs below look close to the inputs.
en = verbalizer.get("en")
en.number("2.6")              # '2.6'
en.unit("0.156", "mm/s")      # '0.156 mm/s'
en.date("2026-07-04")         # '2026-07-04'
en.time(11, 31)               # '11:31'
en.email("a.b@gmail.com")     # 'a dot b at gmail dot com'
en.spell("PV")                # 'P V'

# Polish — the exact same calls, fully verbalized. This is where the value is: a TTS
# engine mangles these, so the plugin produces correct spoken Polish deterministically.
pl = verbalizer.get("pl")
pl.number("2.6")              # 'dwa przecinek sześć'
pl.unit("0.156", "mm/s")      # 'zero przecinek sto pięćdziesiąt sześć milimetra na sekundę'
pl.date("2026-07-04")         # 'sobota, czwartego lipca dwa tysiące dwudziestego szóstego roku'
pl.time(11, 31)               # 'jedenasta trzydzieści jeden'
pl.email("a.b@gmail.com")     # 'a kropka b małpka gmail kropka com'
pl.spell("PV")                # 'pe fau'

verbalizer.available()        # ['en', 'pl']
```

**Full method surface** (override per language; the base is a safe fallback for every one):

| Method | Does | Base behaviour |
|--------|------|----------------|
| `number(value)` | A bare number → words | passthrough (English TTS reads digits) |
| `unit(value, unit)` | Measured value + unit, agreement-correct | `"<number> <unit>"` |
| `date(iso, with_weekday=True, with_year=True)` | ISO date → spoken date | passthrough (returns the ISO) |
| `time(hour, minute)` | 24h clock → spoken time | `"HH:MM"` |
| `email(address)` | Speak an email/identifier via `SEPARATORS` | shared across languages |
| `spell(token)` | Spell a token letter-by-letter via `LETTERS` | bare characters |
| `guidance(glossary=None)` | Per-language LLM speaking rules + optional glossary | generic, language-agnostic rules |

Three **free-text passes** the agent runs over a model-produced reply before TTS (each a no-op
unless the language opts in, so they're safe to run over any string):

| Pass | Rewrites | Gated on | Notes |
|------|----------|----------|-------|
| `measure_text(text)` | every `<number> <unit>` and `<a>-<b> <unit>` range | `MEASURE_UNITS` set | leaves ISO codes, dates, versions, bare numbers untouched |
| `datetime_text(text)` | ISO dates and date-times (`2026-07-01 11:31 UTC`) | `VERBALIZES_DATETIME` | date-times first; leaves a trailing `UTC`/`Z` for `spell_acronyms` |
| `spell_acronyms(text)` | known acronyms → letter-by-letter (`RMS` → `er em es`) | `ACRONYMS` non-empty | case-sensitive, whole-token; never touches lowercase words or unknown all-caps names |

Run them in this order — `measure_text` → `datetime_text` → `spell_acronyms` — so the datetime
pass can hand its trailing `UTC` to the acronym pass. `get(lang)` falls back to English for an
unregistered language, so callers never guard.

## Adding a language

`Verbalizer` is a concrete, language-neutral base — subclass it and override only what differs.
Because the base is a safe fallback, a partial plugin still works; you can ship `number`/`date`
first and fill in the rest later.

```python
from typing import ClassVar
from signalwire.conversation_kit.verbalizer import Verbalizer, register

class GermanVerbalizer(Verbalizer):
    lang: ClassVar[str] = "de"

    # Class attributes drive the shared methods — set these and email()/spell()/
    # measure_text()/spell_acronyms() work without overriding them:
    SEPARATORS: ClassVar[dict[str, str]] = {"@": "at", ".": "Punkt", "-": "Bindestrich"}
    LETTERS: ClassVar[dict[str, str]] = {"a": "a", "b": "be", ...}
    MEASURE_UNITS: ClassVar[tuple[str, ...]] = ("mm/s", "Hz", "°C")
    INSTRUCTION: ClassVar[str] = "Sprich auf Deutsch."
    VERBALIZES_DATETIME: ClassVar[bool] = True     # opt in to date()/time()/datetime_text()
    # ACRONYMS defaults to {DIN, ISO, PPV, RMS, UTC}; override to extend per language.

    def number(self, value): ...
    def date(self, iso, with_weekday=True, with_year=True): ...
    def time(self, hour, minute): ...

register(GermanVerbalizer())     # get("de") now resolves to it
```

Built-in languages (EN, PL) register in `verbalizer/languages/` and are wired up in
`verbalizer/__init__.py`; an application can also `register(...)` its own at runtime without
modifying the SDK. A language is only fully "supported" when three things line up: a verbalizer
plugin, inclusion in the agent's multilingual `allowed` set, and a TTS voice.

## Testing

Unit tests live at the SDK repo root under `tests/unit/conversation_kit/`. From the repo root:

```bash
PYTHONPATH=signalwire python3 -m pytest tests/unit/conversation_kit/ -q
```

`pl.py` is the reference plugin — `tests/unit/conversation_kit/test_verbalizer_pl.py` exercises
cardinals, decimal place-value, unit agreement, dates/times, emails, `measure_text`,
`spell_acronyms`, and `datetime_text`; mirror it when adding a language.

## Invariants (do not break)

These hold the package's "product-agnostic leaf" contract — an agent editing this code must keep
all of them:

- **Zero dependencies.** Standard library only. No third-party imports, ever — it keeps the
  subpackage a self-contained, trivially testable leaf.
- **No SignalWire SDK import.** Even though it ships inside the SDK, `conversation_kit` never
  imports the rest of it. The dependency arrow points one way: the agent imports this.
- **Product-agnostic.** No product names, no business logic, no I/O. The agent supplies product
  wording (e.g. via `guidance()`'s glossary) and wraps these outputs into its own responses.
- **The base is a real fallback.** `Verbalizer()` and `get("<unknown>")` must never raise — they
  return sane English-ish passthrough. New methods on the base need a safe default.
- **Text passes stay no-op-by-default.** `measure_text`/`datetime_text`/`spell_acronyms` return
  the input unchanged unless the relevant class attribute (`MEASURE_UNITS` / `VERBALIZES_DATETIME`
  / `ACRONYMS`) opts in, and must not create false positives on prose, IDs, or versions.

## Design principles

- **Deterministic, not generative** — same input, same output; the model decides *what*, this
  decides the exact value and wording.
- **Zero dependencies** — lightweight, trivially unit-testable.
- **Product-agnostic** — no product names, no business logic, no I/O.
- **Plugin languages** — output is per-language behind one interface; new languages are additive.
