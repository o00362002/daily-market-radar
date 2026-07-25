from __future__ import annotations

import unittest
import urllib.request
from unittest import mock

from radar.adapters.transport import HttpRequest, UrllibHttpTransport


class _Response:
    status = 200
    headers = {"Content-Type": "text/html"}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size: int) -> bytes:
        del size
        return b"<html><body>ok</body></html>"


class UrllibHttpTransportTests(unittest.TestCase):
    def test_redirect_handler_is_a_real_urllib_base_handler(self) -> None:
        opener = mock.Mock()
        opener.open.return_value = _Response()
        with mock.patch("urllib.request.build_opener", return_value=opener) as build_opener:
            response = UrllibHttpTransport().fetch(
                HttpRequest(url="https://example.com/page", timeout_seconds=1)
            )

        handler = build_opener.call_args.args[0]
        self.assertIsInstance(handler, urllib.request.BaseHandler)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, b"<html><body>ok</body></html>")


if __name__ == "__main__":
    unittest.main()
