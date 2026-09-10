"""`signalwire.__version__` must agree with the installed distribution version.

The 3.4.1 release bumped pyproject.toml but not the module attribute, so the
package misreported itself on PyPI. Anything reading __version__ at runtime got
the previous release: a version gate takes the wrong branch, and a bug report
citing it points at the wrong tree. A fallback cannot catch that, because the
attribute is present, just stale.
"""

from importlib.metadata import version

import signalwire


def test_version_attribute_matches_distribution() -> None:
    assert signalwire.__version__ == version("signalwire-sdk")
