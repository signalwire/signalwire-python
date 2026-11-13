"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Speech helpers: text for a voice to say, and what a caller spelled.

The platform normalizes text before its pronunciation rules run, so a bare
number is already words by then, and ``add_pronunciation`` can't make
"10001" read digit by digit. These functions give the words to say instead:
``say_digits``, ``say_last_digits``, ``say_money`` and ``number_words``.
``signalwire.speech.spelling`` reads letters, digits and email addresses a
caller spelled out.
"""

from signalwire.speech.numbers import (
    number_words,
    say_digits,
    say_last_digits,
    say_money,
)

__all__ = ["number_words", "say_digits", "say_last_digits", "say_money"]
