from __future__ import annotations

from collections.abc import Sequence

from radar.contracts.report import RadarReportV2
from radar.contracts.web import PublicationReceiptV1, WebArtifactV1


class NoOpReportPublisher:
    publisher_id = "disabled"

    def publish(
        self,
        report: RadarReportV2,
        artifacts: Sequence[WebArtifactV1],
    ) -> PublicationReceiptV1:
        del report
        return PublicationReceiptV1(
            publisher_id=self.publisher_id,
            status="disabled",
            artifact_paths=[artifact.path for artifact in artifacts],
        )
