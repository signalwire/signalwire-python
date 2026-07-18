"""RequestOptions — the REST request-options envelope (plan 4.2).

A single value object controlling per-request transport behavior: timeout,
retries (with an idempotency-aware retry policy + exponential backoff), and
cooperative cancellation. Supplied at two levels:

- **Client default**: ``RestClient(..., request_options=...)`` stored on the
  ``HttpClient`` and applied to every request.
- **Per-request override**: each verb accepts an optional ``request_options=``
  that *shallow-overrides* the client default for that one call — an unset
  (``None``) field falls back to the client default, then the built-in default.

The timeout + retry semantics are the oracle-pinned, wire-observable contract
(the mock sees N attempts and honors the backoff ordering). ``abort_signal``
fidelity is per-port idiom (see the cross-port design): every port exposes the
field; how deeply the cancellation cuts is the language's business. In python a
sync client cannot interrupt an in-flight blocking socket read without a thread,
so cancellation is checked cooperatively *between* attempts — the honest,
portable minimum.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class _AbortSignal(Protocol):
    """The cooperative-cancellation primitive: anything with ``is_set() -> bool``.

    A ``threading.Event`` satisfies this directly. Checked before each attempt;
    if set, the request raises rather than proceeding.
    """

    def is_set(self) -> bool: ...


# The built-in defaults (the contract floor). ``None`` on a RequestOptions field
# means "inherit"; these are what an unset field resolves to at apply-time.
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_RETRIES = 0
_DEFAULT_RETRY_ON_STATUS = frozenset({429, 500, 502, 503, 504})
_DEFAULT_RETRY_BACKOFF = 0.5


@dataclass(frozen=True)
class RequestOptions:
    """Per-request transport options. All fields optional; ``None`` = inherit.

    Fields (defaults resolved at apply-time, so ``None`` genuinely means
    "fall back to the client default, then the built-in"):

    - ``timeout``: max wall-clock seconds per attempt; on exceed the request
      raises the transport-error type. Built-in default ``30.0``.
    - ``retries``: number of RETRY attempts (total attempts = ``retries + 1``)
      on a retryable failure. Built-in default ``0`` (opt-in resilience — the
      no-retry behavior stays the default; a caller opts into retries).
    - ``retry_on_status``: HTTP statuses that trigger a retry for an idempotent
      method. Built-in ``{429, 500, 502, 503, 504}``.
    - ``retry_backoff``: base seconds for exponential backoff between retries
      (``backoff * 2 ** (attempt - 1)``), honoring ``Retry-After`` when present.
      Built-in ``0.5``.
    - ``abort_signal``: a cooperative-cancellation object (``is_set()``); checked
      before each attempt. Built-in ``None``.
    """

    timeout: float | None = None
    retries: int | None = None
    retry_on_status: frozenset[int] | None = None
    retry_backoff: float | None = None
    abort_signal: _AbortSignal | None = None

    def merge(self, override: RequestOptions | None) -> RequestOptions:
        """Return ``self`` with any set (non-``None``) field of ``override`` applied.

        This is the per-request-over-client-default shallow merge: an unset field
        on ``override`` leaves ``self``'s value intact.
        """
        if override is None:
            return self
        changes: dict[str, Any] = {
            name: value
            for name in (
                "timeout",
                "retries",
                "retry_on_status",
                "retry_backoff",
                "abort_signal",
            )
            if (value := getattr(override, name)) is not None
        }
        return replace(self, **changes)


@dataclass(frozen=True)
class _EffectiveOptions:
    """A RequestOptions with every field resolved to a concrete value.

    Produced by :func:`resolve` — no ``None`` remains, so the request loop reads
    concrete values without re-checking defaults on every attempt.
    """

    timeout: float
    retries: int
    retry_on_status: frozenset[int]
    retry_backoff: float
    abort_signal: _AbortSignal | None


def resolve(
    client_default: RequestOptions | None,
    per_request: RequestOptions | None,
) -> _EffectiveOptions:
    """Resolve the effective options: per-request over client-default over built-in.

    ``None`` on any field inherits the next level down; the built-in defaults are
    the floor. The result has every field concrete.
    """
    merged = (client_default or RequestOptions()).merge(per_request)
    return _EffectiveOptions(
        timeout=merged.timeout if merged.timeout is not None else _DEFAULT_TIMEOUT,
        retries=merged.retries if merged.retries is not None else _DEFAULT_RETRIES,
        retry_on_status=(
            merged.retry_on_status
            if merged.retry_on_status is not None
            else _DEFAULT_RETRY_ON_STATUS
        ),
        retry_backoff=(
            merged.retry_backoff
            if merged.retry_backoff is not None
            else _DEFAULT_RETRY_BACKOFF
        ),
        abort_signal=merged.abort_signal,
    )


# Methods with no server-side side effect — safe to retry on any retryable status.
# POST/PATCH are excluded: they may create/mutate, so they retry ONLY on a
# transport error or 429/503-with-Retry-After (never blindly on 500/502/504),
# to avoid duplicate side effects. This asymmetry is part of the pinned contract.
_IDEMPOTENT_METHODS = frozenset({"GET", "PUT", "DELETE", "HEAD", "OPTIONS"})


def status_is_retryable(method: str, status: int, opts: _EffectiveOptions) -> bool:
    """Whether an HTTP ``status`` for ``method`` should trigger a retry.

    Idempotent methods (GET/PUT/DELETE) retry on the full ``retry_on_status``
    set. Non-idempotent methods (POST/PATCH) retry only on 429/503 (the
    Retry-After-bearing throttles), never on 500/502/504, to avoid replaying a
    side effect that may have partially applied.
    """
    if status not in opts.retry_on_status:
        return False
    if method.upper() in _IDEMPOTENT_METHODS:
        return True
    # Non-idempotent: only the throttle statuses (which carry Retry-After and
    # mean "the request was NOT processed, back off").
    return status in (429, 503)
