"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
The shallow closed-key check and anyOf/oneOf-shaped verb configs.

``_verb_top_level_property_names`` used to test ``body.get("type") != "object"``
on the verb's config node and bail otherwise. A union node (``{"anyOf": [...]}``)
carries no ``type`` of its own, so that test failed and the resolver returned
None — which ``_validate_verb_top_level_keys`` reads as "no key-set to enforce"
and answers valid for ANY key. The check did not report a problem; it stopped
checking and reported success, which is the worse of the two.

Five verbs in the SHIPPED schema.json are union-shaped — connect and play (oneOf
of $refs), send_sms (anyOf of $refs), sleep (anyOf of an object / integer /
SWMLVar), and unset (anyOf of string / array). Four of the five have object
branches whose keys are perfectly enumerable.

The semantic: a config satisfying a union satisfies SOME branch, so the known
keys are the UNION of the object branches' keys, and a key belonging to no branch
belongs to no valid document. Non-object branches contribute nothing (they
constrain the config to not be an object at all — a different question). ``unset``
has no object branch, so it correctly stays disengaged.

NOTE on reachability in this port: ``add_verb`` routes a verb with a registered
HANDLER to this shallow resolver and everything else to the deep full-JSON-Schema
validator. ``ai`` is the only registered handler, and it is a plain closed object,
so the union verbs do not reach the shallow resolver today — the deep path
rejects a stray key. The resolver defect is therefore LATENT in python: it goes
live the moment any union-shaped verb gets a handler. These tests exercise the
resolver directly, which is where the defect lives.
"""

from typing import Any

import pytest

from signalwire.utils.schema_utils import SchemaUtils


# The verb configs the shipped schema expresses as an anyOf/oneOf, with the key
# set the union must resolve to and a legitimate config that must keep passing.
UNION_SHAPED_VERBS: list[tuple[str, str, dict[str, Any], int]] = [
    ("sleep", "duration", {"duration": 5000}, 1),
    ("play", "url", {"url": "https://example.test/a.mp3"}, 8),
    (
        "send_sms",
        "body",
        {"to_number": "+15551110000", "from_number": "+15552220000", "body": "hi"},
        6,
    ),
    ("connect", "to", {"to": "sip:alice@example.test"}, 22),
]

# Shapes that genuinely have no closed key-set, so the fix is not read as
# "always enforce something":
#   set   -- an OPEN object (unevaluatedProperties:{} with no `not`, zero declared
#            properties): a free-form variable bag by design.
#   unset -- a union with no object branch (string | array of string).
#   cond / label / return -- array / string / untyped, not objects at all.
NON_ENUMERABLE_VERBS = ["set", "unset", "cond", "label", "return"]


@pytest.fixture(scope="module")
def schema_utils() -> SchemaUtils:
    """The real shipped schema — this defect is about the vendored schema.json,
    not a synthetic fixture."""
    return SchemaUtils()


class TestUnionShapedVerbs:
    """The union-shaped verb configs the resolver used to bail on."""

    @pytest.mark.parametrize(
        "verb,want_key,legit,want_count",
        UNION_SHAPED_VERBS,
        ids=[v[0] for v in UNION_SHAPED_VERBS],
    )
    def test_union_shaped_verbs_resolve_a_key_set(
        self,
        schema_utils: SchemaUtils,
        verb: str,
        want_key: str,
        legit: dict[str, Any],
        want_count: int,
    ) -> None:
        """The direct negative control: before the fix every one of these
        resolved to None, i.e. the closed-key check was disengaged on them."""
        known = schema_utils._verb_top_level_property_names(verb)
        assert known is not None, (
            f"{verb}: closed-key check DISENGAGED on a union-shaped config; "
            "it must resolve to the union of the object branches' keys"
        )
        assert want_key in known, (
            f"{verb}: resolved key set is missing {want_key!r}; got {sorted(known)}"
        )
        assert len(known) == want_count, (
            f"{verb}: resolved {len(known)} keys, want {want_count}: {sorted(known)}"
        )

    @pytest.mark.parametrize(
        "verb,want_key,legit,want_count",
        UNION_SHAPED_VERBS,
        ids=[v[0] for v in UNION_SHAPED_VERBS],
    )
    def test_union_shaped_verbs_reject_unknown_keys(
        self,
        schema_utils: SchemaUtils,
        verb: str,
        want_key: str,
        legit: dict[str, Any],
        want_count: int,
    ) -> None:
        """The forbidden-key direction: a key present in no branch must be
        rejected. Every one of these was ACCEPTED before the fix."""
        cfg = dict(legit)
        cfg["zzz_not_a_real_key"] = 1
        is_valid, errors = schema_utils._validate_verb_top_level_keys(verb, cfg)
        assert not is_valid, (
            f"{verb}: a key present in no branch was ACCEPTED — the closed-key "
            "check is disengaged on this union-shaped config"
        )
        assert "zzz_not_a_real_key" in " ".join(errors), (
            f"{verb}: rejection must name the offending key; got {errors}"
        )

    @pytest.mark.parametrize(
        "verb,want_key,legit,want_count",
        UNION_SHAPED_VERBS,
        ids=[v[0] for v in UNION_SHAPED_VERBS],
    )
    def test_union_shaped_verbs_accept_legitimate_configs(
        self,
        schema_utils: SchemaUtils,
        verb: str,
        want_key: str,
        legit: dict[str, Any],
        want_count: int,
    ) -> None:
        """The other direction — the fix must not start rejecting valid
        documents. A branch set computed as an INTERSECTION would fail here,
        since a key valid in one branch is absent from the others."""
        is_valid, errors = schema_utils._validate_verb_top_level_keys(verb, legit)
        assert is_valid, f"{verb}: legitimate config rejected: {errors}"

    @pytest.mark.parametrize(
        "discriminator,value",
        [
            ("to", "sip:alice@example.test"),
            ("serial", [{"to": "sip:a@example.test"}]),
            ("parallel", [{"to": "sip:a@example.test"}]),
            ("serial_parallel", [[{"to": "sip:a@example.test"}]]),
        ],
    )
    def test_connect_branch_discriminators_all_accepted(
        self, schema_utils: SchemaUtils, discriminator: str, value: Any
    ) -> None:
        """The union direction tested explicitly rather than only in aggregate:
        connect's four ConnectDevice branches differ only in their discriminating
        key, and all four must be accepted — a branch set computed as an
        INTERSECTION would reject three of them."""
        is_valid, errors = schema_utils._validate_verb_top_level_keys(
            "connect", {discriminator: value}
        )
        assert is_valid, (
            f"connect: branch discriminator {discriminator!r} rejected — the "
            f"branch key sets look INTERSECTED, not unioned: {errors}"
        )


class TestNonEnumerableConfigsStayDisengaged:
    """Pins the shapes that genuinely have no closed key set, so nothing is
    weakened and the fix is not read as 'always enforce something'."""

    @pytest.mark.parametrize("verb", NON_ENUMERABLE_VERBS)
    def test_resolver_stays_disengaged(
        self, schema_utils: SchemaUtils, verb: str
    ) -> None:
        assert schema_utils._verb_top_level_property_names(verb) is None, (
            f"{verb} has no closed key-set in the schema; the shallow check must "
            "stay disengaged rather than invent one"
        )

    @pytest.mark.parametrize("verb", NON_ENUMERABLE_VERBS)
    def test_disengaged_check_is_a_no_op_not_a_rejection(
        self, schema_utils: SchemaUtils, verb: str
    ) -> None:
        is_valid, errors = schema_utils._validate_verb_top_level_keys(
            verb, {"anything": 1}
        )
        assert is_valid, f"{verb}: disengaged check must pass, got {errors}"


class TestRefFollowingStillWorks:
    """Guards the shape the resolver already handled — a single $ref
    (ai -> AIObject) — since the fix rewrote that path into the shared recursive
    resolver."""

    def test_ai_ref_resolves(self, schema_utils: SchemaUtils) -> None:
        known = schema_utils._verb_top_level_property_names("ai")
        assert known is not None, (
            "ai: $ref to AIObject must still resolve to a closed key set"
        )
        for want in ["prompt", "params", "SWAIG"]:
            assert want in known, f"ai: resolved key set is missing {want!r}"


class TestEngagedVerbCount:
    """The aggregate the fix moves: 30 -> 34 engaged verbs, with the four
    newly-engaged ones named. An aggregate-only assertion would let a resolver
    that engaged the WRONG four pass, so both are pinned."""

    def test_engaged_count_and_membership(self, schema_utils: SchemaUtils) -> None:
        engaged = {
            verb
            for verb in schema_utils.verbs
            if schema_utils._verb_top_level_property_names(verb) is not None
        }
        disengaged = set(schema_utils.verbs) - engaged

        assert len(engaged) == 34, (
            f"expected 34 engaged verbs, got {len(engaged)}; "
            f"disengaged = {sorted(disengaged)}"
        )
        # The four union-shaped verbs with object branches, which the pre-fix
        # resolver bailed on.
        for verb in ["sleep", "play", "send_sms", "connect"]:
            assert verb in engaged, f"{verb} must be engaged after the fix"
        # Nothing may be weakened: these five have no closed key-set.
        assert disengaged == set(NON_ENUMERABLE_VERBS), (
            f"the disengaged set must be exactly {sorted(NON_ENUMERABLE_VERBS)}, "
            f"got {sorted(disengaged)}"
        )


class TestResolverTerminates:
    """The depth bound: a self-referential $ref must not spin the resolver."""

    def test_self_referential_ref_terminates(self) -> None:
        su = SchemaUtils()
        # A node that $refs a $def which $refs itself. Without the depth bound
        # this recurses until the interpreter's stack limit.
        su.schema.setdefault("$defs", {})["SelfRef"] = {"$ref": "#/$defs/SelfRef"}
        assert su._closed_key_set({"$ref": "#/$defs/SelfRef"}, 0) is None

    def test_self_referential_union_terminates(self) -> None:
        su = SchemaUtils()
        su.schema.setdefault("$defs", {})["SelfUnion"] = {
            "anyOf": [{"$ref": "#/$defs/SelfUnion"}]
        }
        assert su._closed_key_set({"$ref": "#/$defs/SelfUnion"}, 0) is None
