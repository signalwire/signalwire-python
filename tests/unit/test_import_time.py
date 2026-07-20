"""§6.2-python: `import signalwire` must be LIGHT — no FastAPI/uvicorn/pydantic dragged
at import time (owner decision: no packaging split; import-time behavior only). The
agent/web symbols lazy-resolve on first access (PEP 562)."""

import subprocess
import sys


def test_import_signalwire_is_light() -> None:
    # a fresh interpreter so previously-imported modules can't mask the check
    code = (
        "import sys\n"
        "import signalwire\n"
        "heavy=[m for m in ('fastapi','uvicorn','starlette') "
        "if any(x==m or x.startswith(m+'.') for x in sys.modules)]\n"
        "assert not heavy, f'import signalwire dragged {heavy}'\n"
        "print('LIGHT')\n"
    )
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert p.returncode == 0 and "LIGHT" in p.stdout, p.stdout + p.stderr


def test_lazy_symbols_resolve() -> None:
    code = (
        "from signalwire import AgentBase, FunctionResult, DataMap, SWMLService\n"
        "import signalwire\n"
        "assert 'AgentBase' in dir(signalwire)\n"
        "assert AgentBase.__name__ == 'AgentBase'\n"
        "print('RESOLVED')\n"
    )
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert p.returncode == 0 and "RESOLVED" in p.stdout, p.stdout + p.stderr
