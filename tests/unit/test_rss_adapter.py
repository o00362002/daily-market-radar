import pathlib
import unittest

from radar.adapters.rss import RssAdapter, _parse_feed
from radar.schemas.source import SourceRegistry


ROOT = pathlib.Path(__file__).resolve().parents[2]


class RssAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        registry = SourceRegistry.from_file(ROOT / "config/source_registry.json")
        self.source = registry.get("openai_news")
        self.tw_source = registry.get("ithome_tw")

    def test_legacy_rss_adapter_stays_compatible(self) -> None:
        xml = """<?xml version='1.0'?><rss><channel><item><title>One</title><link>https://example.com/one</link></item></channel></rss>"""
        documents = RssAdapter("fixture", "https://example.com/feed").parse(xml)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].title, "One")

    def test_parse_rss_to_document_with_source_metadata(self) -> None:
        xml = b"""<?xml version='1.0'?><rss><channel><item><title>Agent update</title><link>https://example.com/agent?utm_source=test</link><pubDate>Fri, 10 Jul 2026 08:00:00 GMT</pubDate><description>Details</description></item></channel></rss>"""
        documents = _parse_feed(xml, source=self.source, fetched_at="2026-07-10T09:00:00+00:00", limit=10)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].source_id, "openai_news")
        self.assertEqual(documents[0].url, "https://example.com/agent")
        self.assertEqual(documents[0].primary_domain, "ai_agents_applications")
        self.assertEqual(documents[0].lane, "top_down")

    def test_parse_atom_to_document(self) -> None:
        atom = b"""<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'><entry><title>Atom update</title><link href='https://example.com/atom'/><updated>2026-07-10T08:00:00Z</updated><summary>Summary</summary></entry></feed>"""
        documents = _parse_feed(atom, source=self.source, fetched_at="2026-07-10T09:00:00+00:00", limit=10)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].title, "Atom update")
        self.assertEqual(documents[0].published_at, "2026-07-10T08:00:00+00:00")

    def test_parse_rss_1_rdf_with_namespaced_date(self) -> None:
        rdf = b"""<?xml version='1.0'?>
        <rdf:RDF xmlns='http://purl.org/rss/1.0/'
                 xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                 xmlns:dc='http://purl.org/dc/elements/1.1/'>
          <item rdf:about='https://example.com/rdf'>
            <title>RDF update</title>
            <dc:date>2026-07-10</dc:date><description>Details</description>
          </item>
        </rdf:RDF>"""
        documents = _parse_feed(rdf, source=self.source, fetched_at="2026-07-11T09:00:00+00:00", limit=10)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].title, "RDF update")
        self.assertEqual(documents[0].url, "https://example.com/rdf")
        self.assertEqual(documents[0].published_at, "2026-07-10T00:00:00+00:00")

    def test_parse_iso_date_with_repeated_whitespace(self) -> None:
        xml = b"""<?xml version='1.0'?><rss><channel><item><title>Taiwan update</title><link>https://example.com/tw</link><pubDate>2026-07-11  07:07:37</pubDate></item></channel></rss>"""
        documents = _parse_feed(xml, source=self.tw_source, fetched_at="2026-07-11T09:00:00+00:00", limit=10)
        self.assertEqual(documents[0].published_at, "2026-07-10T23:07:37+00:00")


if __name__ == "__main__":
    unittest.main()
