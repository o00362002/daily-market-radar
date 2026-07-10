from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WebArtifactV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: str
    media_type: str
    content_hash: str
    content: bytes


class PublicationReceiptV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    publisher_id: str
    status: str
    artifact_paths: list[str]
