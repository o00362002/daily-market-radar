from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from radar.contracts.report import RadarReportV2
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1


@runtime_checkable
class StateStore(Protocol):
    def load(self, key: str) -> bytes | None: ...

    def save(self, key: str, value: bytes) -> None: ...


@runtime_checkable
class WebArtifactStore(Protocol):
    def read(self, path: str) -> WebArtifactV1 | None: ...

    def commit(self, artifacts: Sequence[WebArtifactV1]) -> None: ...


@runtime_checkable
class ReportPublisher(Protocol):
    publisher_id: str

    def publish(
        self,
        report: RadarReportV2,
        artifacts: Sequence[WebArtifactV1],
    ) -> PublicationReceiptV1: ...
