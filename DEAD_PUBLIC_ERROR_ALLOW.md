# DEAD-PUBLIC-ERROR allowlist (python — reference)

Each entry excuses one error type that `porting-sdk/scripts/dead_public_error.py`
(DEAD-PUBLIC-ERROR) reports as dead public surface. Form:
`- <ErrorName> — reason (approver, date)`.

- _BlockedAddressError — private to signalwire/utils/url_validator.py and not exported. It is raised from the overridden `_new_conn()` of the connection classes that `_PublicSession` installs, inside urllib3's connect path, so the raise site is necessarily in the defining file. Callers see it wrapped in `requests.exceptions.ConnectionError`, and tests/unit/utils/test_public_session.py covers it (anthm@signalwire.com, 2026-09-24)
