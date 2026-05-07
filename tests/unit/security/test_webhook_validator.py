"""
Tests for ``signalwire.core.security.webhook_validator``.

Cross-language SDK contract: every port must implement Scheme A (hex
HMAC-SHA1 over url+rawBody for JSON/RELAY) and Scheme B (base64 HMAC-SHA1
over url+sortedFormParams for cXML/Compat) per
``porting-sdk/webhooks.md``. This file is the reference test suite —
other ports translate it as-is.

Vectors A, B, C below are the canonical vectors from the spec; if they
break, a port has a real bug — DO NOT relax them.
"""

import base64
import hashlib
import hmac
import inspect

import pytest

from signalwire.core.security.webhook_validator import (
    validate_request,
    validate_webhook_signature,
)


# ---------------------------------------------------------------------------
# Canonical test vectors from porting-sdk/webhooks.md
# ---------------------------------------------------------------------------

VECTOR_A = {
    "signing_key": "PSKtest1234567890abcdef",
    "url": "https://example.ngrok.io/webhook",
    "raw_body": (
        '{"event":"call.state","params":'
        '{"call_id":"abc-123","state":"answered"}}'
    ),
    "expected": "c3c08c1fefaf9ee198a100d5906765a6f394bf0f",
}

VECTOR_B_PARAMS = {
    "CallSid": "CA1234567890ABCDE",
    "Caller": "+14158675309",
    "Digits": "1234",
    "From": "+14158675309",
    "To": "+18005551212",
}
VECTOR_B = {
    "signing_key": "12345",
    "url": "https://mycompany.com/myapp.php?foo=1&bar=2",
    "params": VECTOR_B_PARAMS,
    "expected": "RSOYDt4T1cUTdK1PDd93/VVr8B8=",
}

VECTOR_C = {
    "signing_key": "PSKtest1234567890abcdef",
    "raw_body": '{"event":"call.state"}',
    "url": (
        "https://example.ngrok.io/webhook?bodySHA256="
        "69f3cbfc18e386ef8236cb7008cd5a54b7fed637a8cb3373b5a1591d7f0fd5f4"
    ),
    "expected": "dfO9ek8mxyFtn2nMz24plPmPfIY=",
}


def _form_encoded(params):
    """Build an x-www-form-urlencoded body that round-trips through parse_qsl
    back to the same key/value pairs Scheme B will sort and concat.

    We hand-encode rather than using ``urlencode`` so the test stays close to
    what HTTP middleware would actually see on the wire (``+`` -> ``%2B``).
    """
    from urllib.parse import quote_plus

    return "&".join(f"{quote_plus(k)}={quote_plus(str(v))}" for k, v in params.items())


# ---------------------------------------------------------------------------
# Scheme A — RELAY/JSON (hex)
# ---------------------------------------------------------------------------

class TestSchemeA:
    def test_positive_canonical_vector(self):
        """Vector A: known JSON body + URL + key produces the known hex digest."""
        assert (
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                VECTOR_A["expected"],
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )
            is True
        )

    def test_negative_tampered_body(self):
        """Vector A: same key/url, body changed → returns False."""
        tampered = VECTOR_A["raw_body"].replace("answered", "ringing")
        assert (
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                VECTOR_A["expected"],
                VECTOR_A["url"],
                tampered,
            )
            is False
        )

    def test_negative_wrong_key(self):
        """Different signing key against the same vector → False."""
        assert (
            validate_webhook_signature(
                "wrong-key",
                VECTOR_A["expected"],
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )
            is False
        )

    def test_negative_wrong_url(self):
        """Same body/key, different URL path → False (URL is part of the digest)."""
        assert (
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                VECTOR_A["expected"],
                "https://example.ngrok.io/different",
                VECTOR_A["raw_body"],
            )
            is False
        )


# ---------------------------------------------------------------------------
# Scheme B — Compat/cXML (base64 form)
# ---------------------------------------------------------------------------

class TestSchemeB:
    def test_positive_canonical_form_vector(self):
        """Vector B: form params via raw body → matches the canonical Twilio digest."""
        body = _form_encoded(VECTOR_B["params"])
        assert (
            validate_webhook_signature(
                VECTOR_B["signing_key"],
                VECTOR_B["expected"],
                VECTOR_B["url"],
                body,
            )
            is True
        )

    def test_positive_via_validate_request_dict(self):
        """validate_request(..., dict) goes straight to Scheme B with parsed params."""
        assert (
            validate_request(
                VECTOR_B["signing_key"],
                VECTOR_B["expected"],
                VECTOR_B["url"],
                VECTOR_B["params"],
            )
            is True
        )

    def test_positive_via_validate_request_list_of_tuples(self):
        """validate_request also accepts pre-parsed (key, value) tuples."""
        params_list = list(VECTOR_B["params"].items())
        assert (
            validate_request(
                VECTOR_B["signing_key"],
                VECTOR_B["expected"],
                VECTOR_B["url"],
                params_list,
            )
            is True
        )

    def test_body_sha256_canonical_vector(self):
        """Vector C: JSON body on compat surface, signature over URL with bodySHA256."""
        assert (
            validate_webhook_signature(
                VECTOR_C["signing_key"],
                VECTOR_C["expected"],
                VECTOR_C["url"],
                VECTOR_C["raw_body"],
            )
            is True
        )

    def test_body_sha256_mismatch_rejected(self):
        """If the URL's bodySHA256 doesn't match sha256(raw_body), reject even if HMAC matches."""
        # Recompute a fresh signature over Vector C's URL but pair it with a
        # different body — the HMAC would match URL+'' but the bodySHA256
        # check should fail, so the result must be False.
        wrong_body = '{"event":"DIFFERENT"}'
        assert (
            validate_webhook_signature(
                VECTOR_C["signing_key"],
                VECTOR_C["expected"],
                VECTOR_C["url"],
                wrong_body,
            )
            is False
        )


# ---------------------------------------------------------------------------
# URL port normalization
# ---------------------------------------------------------------------------

class TestUrlPortNormalization:
    def _b64_sig(self, key, url, params=None):
        params = params or {}
        concat = url
        for k in sorted(params.keys()):
            concat += f"{k}{params[k]}"
        return base64.b64encode(
            hmac.new(key.encode(), concat.encode(), hashlib.sha1).digest()
        ).decode()

    def test_signature_with_port_accepted_when_request_has_no_port(self):
        """Backend signed with :443 — request URL has no port → accept."""
        key = "test-key"
        url_with_port = "https://example.com:443/webhook"
        url_without_port = "https://example.com/webhook"
        sig = self._b64_sig(key, url_with_port)
        # raw_body is a non-form body; Scheme B falls back to empty params.
        assert (
            validate_webhook_signature(key, sig, url_without_port, "{}")
            is True
        )

    def test_signature_without_port_accepted_when_request_has_standard_port(self):
        """Backend signed without port — request URL has :443 → accept."""
        key = "test-key"
        url_with_port = "https://example.com:443/webhook"
        url_without_port = "https://example.com/webhook"
        sig = self._b64_sig(key, url_without_port)
        assert (
            validate_webhook_signature(key, sig, url_with_port, "{}")
            is True
        )

    def test_http_port_80_normalization(self):
        """http + :80 mirrors https + :443."""
        key = "test-key"
        url_with_port = "http://example.com:80/path"
        url_without_port = "http://example.com/path"
        sig = self._b64_sig(key, url_with_port)
        assert (
            validate_webhook_signature(key, sig, url_without_port, "")
            is True
        )


# ---------------------------------------------------------------------------
# Repeated form keys
# ---------------------------------------------------------------------------

class TestRepeatedFormKeys:
    def test_repeated_keys_concat_in_submission_order(self):
        """``To=a&To=b`` → signing string ``URL + ToaTob``, deterministic."""
        key = "test-key"
        url = "https://example.com/hook"
        body = "To=a&To=b"
        # Expected concat: ``ToaTob`` (sorted by key only; preserve order within).
        expected_data = url + "ToaTob"
        sig = base64.b64encode(
            hmac.new(key.encode(), expected_data.encode(), hashlib.sha1).digest()
        ).decode()
        assert (
            validate_webhook_signature(key, sig, url, body)
            is True
        )

    def test_repeated_keys_swapped_order_is_a_different_signature(self):
        """``To=b&To=a`` is a different submission and yields a different digest."""
        key = "test-key"
        url = "https://example.com/hook"
        body_ab = "To=a&To=b"
        body_ba = "To=b&To=a"
        # Sign for body_ab, then verify body_ba doesn't match — proves order
        # within repeated keys is honored, not lexically sorted.
        data_ab = url + "ToaTob"
        sig_for_ab = base64.b64encode(
            hmac.new(key.encode(), data_ab.encode(), hashlib.sha1).digest()
        ).decode()
        assert validate_webhook_signature(key, sig_for_ab, url, body_ab) is True
        assert validate_webhook_signature(key, sig_for_ab, url, body_ba) is False


# ---------------------------------------------------------------------------
# Error modes
# ---------------------------------------------------------------------------

class TestErrorModes:
    def test_missing_signature_returns_false(self):
        """Empty / None signature header → False, no exception."""
        assert (
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                "",
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )
            is False
        )
        assert (
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                None,  # type: ignore[arg-type]
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )
            is False
        )

    def test_missing_signing_key_raises_value_error(self):
        """Empty / None signing key → ValueError (programming error)."""
        with pytest.raises(ValueError):
            validate_webhook_signature("", "sig", VECTOR_A["url"], VECTOR_A["raw_body"])
        with pytest.raises(ValueError):
            validate_webhook_signature(
                None,  # type: ignore[arg-type]
                "sig",
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )

    def test_non_string_raw_body_raises_type_error(self):
        """A parsed dict mistakenly passed as raw_body → TypeError."""
        with pytest.raises(TypeError):
            validate_webhook_signature(
                VECTOR_A["signing_key"],
                "sig",
                VECTOR_A["url"],
                {"event": "call.state"},  # type: ignore[arg-type]
            )

    def test_malformed_signature_returns_false_without_throwing(self):
        """Garbage signature string → False, no exception."""
        # Wrong length, weird chars, base64 noise — none should throw.
        for garbage in ("xyz", "!!!!", "a" * 100, "%%notbase64%%"):
            assert (
                validate_webhook_signature(
                    VECTOR_A["signing_key"],
                    garbage,
                    VECTOR_A["url"],
                    VECTOR_A["raw_body"],
                )
                is False
            )


# ---------------------------------------------------------------------------
# validate_request legacy alias dispatch
# ---------------------------------------------------------------------------

class TestValidateRequestDispatch:
    def test_string_arg_delegates_to_combined_validator(self):
        """A string 4th arg behaves identically to validate_webhook_signature."""
        assert (
            validate_request(
                VECTOR_A["signing_key"],
                VECTOR_A["expected"],
                VECTOR_A["url"],
                VECTOR_A["raw_body"],
            )
            is True
        )

    def test_dict_arg_runs_scheme_b_directly(self):
        """A dict 4th arg goes straight to Scheme B with parsed params."""
        assert (
            validate_request(
                VECTOR_B["signing_key"],
                VECTOR_B["expected"],
                VECTOR_B["url"],
                VECTOR_B["params"],
            )
            is True
        )

    def test_invalid_arg_type_raises_type_error(self):
        """Anything other than str/mapping/list raises TypeError."""
        with pytest.raises(TypeError):
            validate_request(
                VECTOR_A["signing_key"],
                "sig",
                VECTOR_A["url"],
                42,  # type: ignore[arg-type]
            )


# ---------------------------------------------------------------------------
# Constant-time compare — read the source, not just the result
# ---------------------------------------------------------------------------

class TestConstantTimeCompare:
    def test_validator_source_uses_hmac_compare_digest(self):
        """The implementation must call ``hmac.compare_digest`` for all sig comparisons.

        We read the source rather than time-measuring because timing tests are
        flaky in CI and the porting-sdk spec explicitly names the function to use.
        Other ports do the equivalent (``crypto.timingSafeEqual`` in Node, etc.).
        """
        from signalwire.core.security import webhook_validator

        src = inspect.getsource(webhook_validator)
        assert "hmac.compare_digest" in src, (
            "webhook_validator must use hmac.compare_digest for signature compare"
        )
        # And it must NOT use plain == on the expected/actual digest.
        # Allow == elsewhere (e.g. parameter defaults), but not the literal
        # ``expected_a == signature`` / ``expected_b == signature`` patterns.
        assert "expected_a == signature" not in src
        assert "expected_b == signature" not in src
