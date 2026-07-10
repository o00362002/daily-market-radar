from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree

from radar.domain.models import Document


@dataclass(frozen=True)
class RssAdapter:
    source_id: str
    feed_url: str

    def parse(self, xml_text: str) -> list[Document]:
        root = ElementTree.fromstring(xml_text)
        documents: list[Document] = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or "Untitled"
            link = item.findtext("link") or self.feed_url
            documents.append(Document.fixture(source_id=self.source_id, url=link, title=title))
        return documents
