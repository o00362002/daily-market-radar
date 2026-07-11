import pathlib
import unittest

from radar.schemas.source import SourceAdapter, SourceAdapterConfig, SourceRegistry


ROOT = pathlib.Path(__file__).resolve().parents[2]


class SourceRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SourceRegistry.from_file(ROOT / "config/source_registry.json")

    def test_registry_requires_unique_source_and_canonical_urls(self) -> None:
        self.registry.validate()
        source_ids = [source.source_id for source in self.registry.sources]
        canonical_urls = [source.canonical_url for source in self.registry.sources]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(len(canonical_urls), len(set(canonical_urls)))

    def test_legacy_source_adapter_config_import_remains_available(self) -> None:
        self.assertIs(SourceAdapter, SourceAdapterConfig)

    def test_adapters_are_nested_under_entity_sources(self) -> None:
        openai = self.registry.get("openai_news")
        self.assertIn("openai_news_rss", openai.aliases)
        self.assertEqual(openai.adapters[0].kind, "rss")
        self.assertEqual(openai.adapters[0].url, "https://openai.com/news/rss.xml")

    def test_opml_projection_has_no_drift(self) -> None:
        expected = (ROOT / "FRESHRSS_SEEDS.opml").read_text(encoding="utf-8")
        self.assertEqual(self.registry.to_opml(), expected)

    def test_non_feed_sources_do_not_change_opml_projection(self) -> None:
        opml = self.registry.to_opml()
        self.assertNotIn("Anthropic News", opml)
        self.assertNotIn("金融監督管理委員會", opml)
        self.assertIn("OpenAI News RSS", opml)

    def test_taiwan_and_niche_sources_are_registered(self) -> None:
        for source_id in ("twse", "fsc_tw", "dgbas_tw", "vogue_taiwan", "cryptocity_tw", "blocktrend_tw"):
            self.assertEqual(self.registry.get(source_id).macro_region, "Taiwan")

    def test_expanded_regional_and_primary_sources_have_executable_feeds(self) -> None:
        for source_id in (
            "dgbas_tw",
            "pts_tw",
            "abmedia_tw",
            "blocktempo_tw",
            "digitimes_asia",
            "sec_press",
            "ethereum_foundation_blog",
            "aws_ml_blog",
            "adb_news",
            "wto_news",
            "asean_news",
            "africanews",
            "abc_australia_business",
            "channel_news_asia",
            "the_hindu_business",
            "glossy_retail",
        ):
            source = self.registry.get(source_id)
            self.assertTrue(any(adapter.kind == "rss" for adapter in source.adapters), source_id)

        self.assertEqual(
            next(adapter.url for adapter in self.registry.get("blocktrend_tw").adapters if adapter.kind == "rss"),
            "https://www.blocktrend.today/feed",
        )


if __name__ == "__main__":
    unittest.main()
