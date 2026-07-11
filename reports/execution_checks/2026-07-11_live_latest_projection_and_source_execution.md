# Live latest projection and source execution repair

Date: 2026-07-11  
Scope: GitHub Pages same-day latest selection, executable source coverage, feed parsing

## Root cause

The production database already contained newer same-day reports with 972 and 956 items, but the web projection sorted reports by `(date, run_id)` before de-duplicating the date. `run_id` is a content hash, not a timestamp, so the older 3-item report sorted last and was deployed successfully as `latest.json`.

Separately, registered Nikkei Asia and Nature feeds use RSS 1.0/RDF and silently produced zero documents under the RSS 2.0-only parser. iThome timestamps with repeated whitespace fell back to fetch time, and Blocktrend's redirecting Substack URL failed from GitHub Actions.

## Repair

- Preserve durable repository write order when choosing the final report for a date; add a regression where the newer run ID sorts lexicographically before the older ID.
- Parse RSS 2.0, namespaced RSS 1.0/RDF and Atom; use `rdf:about` as the RSS 1.0 link fallback.
- Normalize repeated date whitespace and interpret naïve Taiwan-source timestamps in Asia/Taipei before storing UTC.
- Use Blocktrend's direct canonical feed.
- Upgrade DGBAS from web-only to executable official RSS and add live-probed Taiwan, primary-source, retail and regional feeds across Africa, Asia-Pacific, Oceania, South Asia and Southeast Asia.

## Evidence

- Production-state export selects `run_3f0321c790a7`: 956 items, 725 Major, 231 Potential, 207 Taiwan, 38 checked sources.
- Expanded registry live probe: 69 registered, 54 RSS-capable checked, 1,525 documents, 360 Taiwan documents, zero failures; only RSSHub releases and arXiv cs.LG were empty.
- Fresh-database end-to-end live run: 1,521 items, 1,249 Major, 272 Potential, 357 Taiwan, 54 checked sources, zero source failures.
- Targeted regression suite covers same-day write order, RSS 1.0/RDF, RDF link fallback, repeated-whitespace Taiwan dates and executable source identities.

## Five-line receipt

改了什麼：修正同日最新版選錯、補 RSS 1.0/RDF 與台灣日期解析，並把實測來源接入每日 runtime。  
機器檢查：production-state export、真實 54-source probe、fresh DB live run、targeted tests 與 repo validation。  
沒做什麼：沒有把 generic search 當來源、沒有宣稱 social/API/query-recipe/外部 discovery 已完成。  
會影響誰：GitHub Pages 今日頁、完整報告、台灣直接證據、跨區域來源覆蓋與後續每日排程。  
你可以驗證：執行 `make validate`，再以 radar-state DB 執行 `radar export-web`，確認 latest run 不再是 3-item run。
