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
    """Also install the documentation in the package, under signalwire/_docs/."""

    def _docs(self) -> list[tuple[str, Path, Path]]:
        target = Path(self.build_lib) / "signalwire" / "_docs"
        return [
            (rel, ROOT / rel, target / rel) for rel in _bundle["iter_doc_files"](ROOT)
        ]

    def run(self) -> None:
        super().run()
        for rel, source, dest in self._docs():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if rel.endswith(".md"):
                with source.open(encoding="utf-8", newline="") as f:
                    text = f.read()
                with dest.open("w", encoding="utf-8", newline="") as f:
                    f.write(_bundle["installed_text"](rel, text))
            else:
                shutil.copy2(source, dest)

    # Declared as outputs, so editable installs that link the build's files
    # include the docs too
    def get_outputs(self, include_bytecode: bool = True) -> list[str]:
        docs = [str(dest) for _, _, dest in self._docs()]
        return [*super().get_outputs(include_bytecode), *docs]

    def get_output_mapping(self) -> dict[str, str]:
        mapping = super().get_output_mapping()
        mapping.update({str(dest): str(source) for _, source, dest in self._docs()})
        return mapping


setup(cmdclass={"build_py": BuildPyWithDocs})
