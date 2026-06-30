# Typed Input Skill

Collect a value the caller **types** on an on-screen keypad — an email, phone number, account
number, anything speech-to-text can't capture reliably. Add one instance per field.

## How it works

1. `request_<field>` speaks a short "type it on your screen" line, emits an `input_request` user
   event (a connected client reveals + focuses the field), and parks via `wait_for_user` until
   the caller submits.
2. The client posts the typed value into `global_data['typed_<field>']`.
3. `confirm_<field>` reads that raw value back, validates it, reopens the keypad if it is missing
   or invalid, otherwise reads it back for the caller to confirm.

The value is never a model argument, so the model can't silently alter or "correct" a typo.
Validation, the user-event payload, and the spoken read-back come from `signalwire.conversation_kit`.

## Requirements

- **Packages**: none (uses `signalwire.conversation_kit`, part of the SDK).
- A connected client that listens for the `input_request` user event and posts the typed value
  back into `global_data['typed_<field>']`.

## Parameters

- `field` (string, **required**) — field key, e.g. `installer_email`. Tools become
  `request_<field>` / `confirm_<field>`; the typed value lands in `global_data['typed_<field>']`.
- `input_type` (string, default `text`) — one of `email`, `phone`, `number`, `text`. Drives
  validation and the read-back form (an email is read as words; anything else is spelled out).
- `open_prompt` (object, **required**) — per-language map `{lang: text}` spoken when the keypad opens.
- `field_label` (object, **required**) — per-language map of the on-screen field label.
- `invalid_prompt` (object, **required**) — per-language map spoken when the typed value fails
  validation, before the keypad reopens.

Prompts resolve against `global_data['language']` at call time (falling back to `en`), so a single
instance serves a multilingual agent.

## Multiple instances

Add it once per field; each instance gets its own `request_`/`confirm_` tools.

```python
agent.add_skill("typed_input", {
    "field": "installer_email",
    "input_type": "email",
    "open_prompt": {
        "en": "Please type the email on your screen.",
        "pl": "Wpisz adres e-mail na ekranie.",
    },
    "field_label": {"en": "Installer's email", "pl": "Adres e-mail instalatora"},
    "invalid_prompt": {
        "en": "That does not look like a valid email; please type it again.",
        "pl": "To nie wygląda na poprawny adres; wpisz go ponownie.",
    },
})
```

## Tools created

- `request_<field>` — open the keypad and wait for the typed value.
- `confirm_<field>` — validate and read back the typed value (reopens the keypad on missing/invalid).
