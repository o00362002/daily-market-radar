import unittest

from radar.adapters.base import UrlPolicy, validate_response_size


class SecurityTests(unittest.TestCase):
    def test_blocks_private_loopback_and_metadata_urls(self) -> None:
        policy = UrlPolicy(allow_internal_hosts={"rsshub"})
        for url in [
            "http://localhost:1200/feed",
            "http://127.0.0.1:8080",
            "http://10.0.0.4/feed",
            "http://169.254.169.254/latest/meta-data",
            "file:///etc/passwd",
        ]:
            with self.subTest(url=url):
                self.assertFalse(policy.is_allowed(url))

    def test_allows_configured_internal_rsshub_host_only(self) -> None:
        policy = UrlPolicy(allow_internal_hosts={"rsshub"})
        self.assertTrue(policy.is_allowed("http://rsshub:1200/github/releases"))
        self.assertFalse(policy.is_allowed("http://redis:6379/"))

    def test_redirect_target_is_rechecked(self) -> None:
        policy = UrlPolicy(allow_internal_hosts={"rsshub"})
        self.assertFalse(
            policy.validate_redirect_chain(
                ["https://example.com/feed", "http://127.0.0.1/admin"]
            )
        )

    def test_response_size_limit(self) -> None:
        validate_response_size(1024, max_bytes=2048)
        with self.assertRaises(ValueError):
            validate_response_size(4096, max_bytes=2048)


if __name__ == "__main__":
    unittest.main()
