"""Secret redaction for logs and receipts.

Passwords, API keys, auth headers and database credentials must never be logged.
`redact` scrubs both known secret values (e.g. the actual env values) and common
secret-shaped patterns, so an accidental interpolation cannot leak a credential.
"""

from __future__ import annotations

import re

REDACTED = "***REDACTED***"

# Env var names whose values are always secret.
SECRET_ENV_NAMES = (
    "OPENAI_API_KEY",
    "FRESHRSS_API_PASSWORD",
    "FRESHRSS_USERNAME",
    "DATABASE_URL",
    "GITHUB_TOKEN",
    "GH_TOKEN",
)

_PATTERNS = [
    # Bearer / GoogleLogin / generic Authorization tokens (whole header value).
    re.compile(r"(?i)(authorization\s*[:=]\s*)(.+)"),
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._\-]+)"),
    re.compile(r"(?i)(googlelogin\s+auth=)([A-Za-z0-9._\-/]+)"),
    # OpenAI-style keys, GitHub tokens.
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    # Credentials embedded in connection strings: scheme://user:password@host
    re.compile(r"(?i)([a-z][a-z0-9+.\-]*://[^:/@\s]+:)([^@/\s]+)(@)"),
    # apikey / token / password query params or key=value pairs.
    re.compile(r"(?i)((?:api[_-]?key|apikey|token|password|passwd|secret)\s*[=:]\s*)([^\s&'\"]+)"),
]


def redact(text: str, secret_values: object = None) -> str:
    """Return ``text`` with known secret values and secret-shaped patterns removed."""

    if text is None:
        return text
    result = str(text)
    for value in secret_values or ():
        if value:
            result = result.replace(str(value), REDACTED)
    for pattern in _PATTERNS:
        if pattern.groups >= 2:
            result = pattern.sub(lambda m: f"{m.group(1)}{REDACTED}" + (m.group(3) if pattern.groups >= 3 else ""), result)
        else:
            result = pattern.sub(REDACTED, result)
    return result


def redact_env(text: str, env: object) -> str:
    """Redact using the actual values of the known secret env vars."""

    getter = env.get if hasattr(env, "get") else (lambda _name: None)
    values = [getter(name) for name in SECRET_ENV_NAMES]
    return redact(text, [value for value in values if value])
