# AI interpretation, translation, future trends and linked indicators

## 改了什麼

- 新增獨立 `AIAnalysisV1` contract，不修改 `RadarReportV2` 事實層。
- 新增受約束的 OpenAI Responses API structured-output enhancer。
- 新增 deterministic fallback，無 API key 或模型失敗仍可輸出。
- 新增六個透明公式連動指標，支援與前一期比較。
- 新增 `/analysis` 選單與頁面，顯示模型、資料版本、prompt、hash、fallback 與來源事件。
- 新增 post-run GitHub Actions，自動在 daily/import 完成後生成並部署 AI 解讀頁。

## 機器檢查

待 PR CI 執行：

- runtime-check
- web-check
- mount-check
- AIAnalysisV1 unit tests
- workflow YAML contract tests
- Astro typecheck/build

## 沒做什麼

- AI 不得改寫原始 RadarReportV2。
- AI 不得修改指標分數、公式、方向或來源事件。
- 趨勢是有條件情境，不是確定預測或投資建議。
- 本次不建立公開聊天介面；「問雷達」留待 read-only MCP 階段。
- 分析歷史目前隨每次最新 durable state 重新產生，尚未建立獨立長期 analysis repository。

## 會影響誰

- GitHub Pages 新增 AI 解讀選單與頁面。
- 有 `OPENAI_API_KEY` 時使用模型語意增強；沒有 key 時顯示 deterministic fallback。
- 每次 `daily-intelligence` 或 `import-chat` 成功後會再執行一次 AI analysis 部署工作流。

## 你可以驗證

```bash
PYTHONPATH=src python -m radar.analysis.cli \
  --database data/radar.db \
  --output-dir artifacts/web/v1/ai-analysis \
  --mode deterministic

cd web
RADAR_ARTIFACTS_DIR=../artifacts/web/v1 npm run types:check
RADAR_ARTIFACTS_DIR=../artifacts/web/v1 npm run build
```

網站檢查：

```text
/analysis
/data/ai-analysis/latest.json
/data/ai-analysis/schema.json
```
