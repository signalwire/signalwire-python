"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

verbalizer — language-agnostic, TTS-ready verbalization with language plugins.

    from signalwire.conversation_kit.verbalizer import get
    v = get("pl")
    v.number("2.6")               # 'dwa przecinek sześć'
    v.unit("0.156", "mm/s")       # 'zero przecinek sto pięćdziesiąt sześć milimetra na sekundę'
    v.date("2026-07-04")          # 'sobota, czwartego lipca dwa tysiące dwudziestego szóstego roku'
    v.email("a.b@gmail.com")      # 'a kropka b małpka gmail kropka com'

Zero dependencies. Add a language by subclassing `Verbalizer`
and calling `register(MyVerbalizer())`.
"""

from __future__ import annotations

from .base import Numeric, Verbalizer
from .registry import available, get, register
from .languages.en import EnglishVerbalizer
from .languages.pl import PolishVerbalizer

register(EnglishVerbalizer())
register(PolishVerbalizer())

__all__ = [
    "EnglishVerbalizer",
    "Numeric",
    "PolishVerbalizer",
    "Verbalizer",
    "available",
    "get",
    "register",
]
