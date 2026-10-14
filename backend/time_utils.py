"""
CineMatrix Studio — UTC time helpers.

``datetime.datetime.utcnow()`` is deprecated (Python 3.12+). These helpers keep its
exact semantics: a *naive* datetime holding UTC wall-clock time. That way existing
SQLite rows, log lines, and comparisons are unaffected, since mixing naive and aware
datetimes raises ``TypeError``.
"""
import datetime


def utc_now() -> datetime.datetime:
    """Current UTC time as a naive datetime (drop-in replacement for ``utcnow()``)."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def utc_now_iso() -> str:
    """Current UTC time in ISO-8601 without an offset, matching ``utcnow().isoformat()``."""
    return utc_now().isoformat()
