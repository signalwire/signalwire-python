"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Tests for signalwire.conversation_kit.inputs — typed-input validation + payload.
"""

from signalwire.conversation_kit import (
    input_request_payload,
    is_valid_email,
    is_valid_number,
    is_valid_phone,
    validate_input,
)


def test_email():
    assert is_valid_email("karolczyk.jakub@gmail.com")
    assert is_valid_email("a@b.co")
    # A valid-format typo is still valid format (only the human read-back catches it).
    assert is_valid_email("karolczyk.jakib@gmail.com")
    assert not is_valid_email("karolczyk.jakib")  # no @
    assert not is_valid_email("jakub@gmail")  # no TLD dot
    assert not is_valid_email("a b@gmail.com")  # space
    assert not is_valid_email("")


def test_phone():
    assert is_valid_phone("+48 600 700 800")
    assert is_valid_phone("1234567")
    assert not is_valid_phone("12345")  # too short
    assert not is_valid_phone("")


def test_number():
    assert is_valid_number("42")
    assert is_valid_number("3,14")  # PL decimal comma
    assert is_valid_number("3.14")
    assert not is_valid_number("abc")
    assert not is_valid_number("")
    # float() parses these, but the verbalizer can't speak them -> reject as invalid.
    assert not is_valid_number("nan")
    assert not is_valid_number("inf")
    assert not is_valid_number("-inf")


def test_validate_input_dispatch():
    assert validate_input("a@b.co", "email")
    assert not validate_input("nope", "email")
    assert validate_input("+48600700800", "tel")
    # Unknown type accepts any non-empty, rejects empty.
    assert validate_input("anything", "text")
    assert not validate_input("", "text")
    assert not validate_input("   ", "email")


def test_input_request_payload():
    p = input_request_payload("typed_installer_email", "Installer email", "email")
    assert p == {
        "type": "input_request",
        "field": "typed_installer_email",
        "label": "Installer email",
        "input_type": "email",
    }
    # Defaults.
    assert input_request_payload("x")["input_type"] == "text"
