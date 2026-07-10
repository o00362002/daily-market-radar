"""Social direct-channel adapters.

First version implements only public, policy-clean direct channels: public RSS,
public Atom, YouTube public feeds and registry-defined public channel URLs. X /
Meta / Threads / Instagram get an official-API adapter *interface* only; without
credentials they are ``unavailable``. A generic web result is never marked as a
direct-channel check, and platform limits are never bypassed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, runtime_checkable

from radar.adapters.transport import HttpRequest, HttpTransport
from radar.ports.sources import CredentialsStatusV1

_YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


@dataclass(frozen=True)
class DirectChannelCheck:
    channel_id: str
    kind: str  # public_rss | public_atom | youtube_public
    direct_checked: bool
    url: str


class PublicSocialChannelAdapter:
    """Public RSS/Atom/YouTube channels — direct-checked, no credentials needed."""

    adapter_id = "public_social_channels"

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    @staticmethod
    def youtube_feed_url(channel_id: str) -> str:
        return _YOUTUBE_FEED.format(channel_id=channel_id)

    def check(self, channel_id: str, url: str, *, kind: str) -> DirectChannelCheck:
        if kind not in {"public_rss", "public_atom", "youtube_public"}:
            raise ValueError(f"unsupported public channel kind: {kind}")
        response = self._transport.fetch(HttpRequest(url=url))
        return DirectChannelCheck(
            channel_id=channel_id,
            kind=kind,
            direct_checked=bool(response.body),
            url=url,
        )


@runtime_checkable
class OfficialSocialApi(Protocol):
    """Interface for authenticated platform APIs (X / Meta / Threads / Instagram)."""

    platform: str

    def credentials_status(self) -> CredentialsStatusV1: ...


@dataclass(frozen=True)
class OfficialSocialApiAdapter:
    """Credential-gated official API stub. Unavailable without credentials.

    Never bypasses platform limits; a generic web search result is not a direct
    channel check and must not be labelled ``direct_checked``.
    """

    platform: str
    secret_env: str
    env: Callable[[str], str | None]

    def credentials_status(self) -> CredentialsStatusV1:
        if not self.env(self.secret_env):
            return CredentialsStatusV1(
                available=False,
                reason=f"{self.platform} official API credential {self.secret_env} unavailable",
            )
        return CredentialsStatusV1(available=True)

    def direct_checked(self) -> bool:
        # Without credentials the platform cannot be directly checked, and a
        # generic web result never counts as a direct channel check.
        return self.credentials_status().available
