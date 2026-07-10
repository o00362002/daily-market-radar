from __future__ import annotations

import unittest

from radar.observability.redaction import REDACTED, redact, redact_env


class RedactionTests(unittest.TestCase):
    def test_known_secret_values_are_removed(self) -> None:
        out = redact("key is sk-super-secret-value-1234567890 done", ["sk-super-secret-value-1234567890"])
        self.assertNotIn("super-secret-value", out)
        self.assertIn(REDACTED, out)

    def test_authorization_header_is_redacted(self) -> None:
        out = redact("Authorization: Bearer abcDEF123456ghijk")
        self.assertNotIn("abcDEF123456ghijk", out)

    def test_googlelogin_and_openai_and_github_tokens(self) -> None:
        self.assertNotIn("tok123456", redact("GoogleLogin auth=tok123456ABCDEF"))
        self.assertNotIn("sk-", redact("sk-abcdefghijklmnop1234567890").replace(REDACTED, ""))
        self.assertNotIn("ghp_", redact("ghp_abcdefghijklmnopqrstuvwxyz0123456789").replace(REDACTED, ""))

    def test_database_url_password_is_redacted(self) -> None:
        out = redact("DATABASE_URL=postgres://radar:topsecretpw@db.internal:5432/radar")
        self.assertNotIn("topsecretpw", out)

    def test_query_param_secrets_redacted(self) -> None:
        out = redact("https://api.example/data?apikey=LEAKED_KEY_123&page=1")
        self.assertNotIn("LEAKED_KEY_123", out)
        self.assertIn("page=1", out)

    def test_redact_env_uses_actual_values(self) -> None:
        env = {"OPENAI_API_KEY": "sk-live-XXYYZZ", "FRESHRSS_API_PASSWORD": "hunter2pw"}
        out = redact_env("connecting with sk-live-XXYYZZ and hunter2pw", env)
        self.assertNotIn("sk-live-XXYYZZ", out)
        self.assertNotIn("hunter2pw", out)

    def test_nonsecret_text_is_preserved(self) -> None:
        self.assertEqual(redact("just a normal log line about coverage gaps"), "just a normal log line about coverage gaps")


if __name__ == "__main__":
    unittest.main()
