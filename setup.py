#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import runpy
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent

# Which repository files ship as documentation: the same list sw-pydocs uses
_bundle = runpy.run_path(str(ROOT / "signalwire/signalwire/cli/pydocs/_bundle.py"))


class BuildPyWithDocs(build_py):
    """Also copy the documentation into the package, under signalwire/_docs/."""

    def run(self) -> None:
        super().run()
        target = Path(self.build_lib) / "signalwire" / "_docs"
        for rel in _bundle["iter_doc_files"](ROOT):
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)


setup(cmdclass={"build_py": BuildPyWithDocs})
