from __future__ import annotations

from collections.abc import Sequence

from radar.contracts.web import WebArtifactV1


class InMemoryStateStore:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    def load(self, key: str) -> bytes | None:
        return self.values.get(key)

    def save(self, key: str, value: bytes) -> None:
        self.values[key] = bytes(value)


class InMemoryWebArtifactStore:
    def __init__(self) -> None:
        self.artifacts: dict[str, WebArtifactV1] = {}

    def read(self, path: str) -> WebArtifactV1 | None:
        return self.artifacts.get(path)

    def commit(self, artifacts: Sequence[WebArtifactV1]) -> None:
        staged = {artifact.path: artifact for artifact in artifacts}
        self.artifacts.update(staged)
