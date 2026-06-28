# Daily Market Radar

這個專案是「全球每日市場情報雷達系統」的版本控管中心，不是單純存放新聞摘要。

每日播報在執行前，應先讀取本 repo 的入口層、雷達清單、固定指標追蹤、科技發展雷達、特殊應用雷達、搜尋 retry 規則、漏抓案例、歷史報告與回測規則，再進行多語言搜尋與交叉驗證。

## 核心定位

- 不是新聞摘要器。
- 不是只挑幾則主觀重要新聞的編輯。
- 不是只整理主流媒體已經大量報導的大眾新聞。
- 是一套「雷達覆蓋 + 固定指標追蹤 + 全球特殊應用搜尋 + 搜尋 retry + 證據分級 + 科技發展路徑 + 回測補漏」的每日市場情報系統。
- 目標是同時捕捉：
  - 全球大趨勢
  - 資金與政策變化
  - 產業結構變化
  - AI 工作流替代
  - AI 產品用量經濟：token / credit / quota / pricing / promo / gift / transfer
  - 科技發展與突破：這是獨立主雷達，包含 AI 驅動突破，也包含非 AI 的單獨科技突破，例如生物、物理、化學、材料、能源、機器人、半導體、醫療、製造、太空、量子等
  - 加密與鏈上資金流
  - 零售、品牌、消費、社群、流行與服飾訊號
  - 全球特殊應用、非主流案例、地方試點、早期商業模式、研究原型、開發者工具與社群弱訊號
  - 早期弱訊號與候選訊號
  - 台灣產業映射
  - 舊版 / 新版播報補漏比對
  - 全指標總和彙總結果

## AI Project OS 入口層

本 repo 已採用 `Reference-Implementation-of-AI-Project-Operating-System` 的核心入口層：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
```

其中 `HIGH_LEVEL_INDEX.md` 是高階脈絡索引，用來避免單點回答、漏掉固定雷達或引用舊規則。

## 每日執行順序

1. 讀取 `SYSTEM_PROMPT.md`
2. 讀取 `PROJECT_MAP.md`
3. 讀取 `HIGH_LEVEL_INDEX.md`
4. 讀取 `CURRENT_STATE.md`
5. 讀取 `CURRENT_DECISIONS.md`
6. 讀取 `configs/radars.yml`
7. 讀取 `configs/triggers.yml`
8. 讀取 `configs/evidence.yml`
9. 讀取 `configs/source_strategy.md`
10. 讀取 `configs/indicator_tracking.yml`
11. 讀取 `configs/technology_development.yml`
12. 讀取 `configs/edge_case_discovery.yml`
13. 讀取 `configs/search_retry_protocol.yml`
14. 讀取 `memory/missed_cases.md`
15. 讀取 `memory/watchlist.md`
16. 讀取近期 `reports/` 內的歷史報告，避免跨日重複與漏抓
17. 使用 `templates/daily_report_template.md` 產出每日報告
18. 使用 `templates/final_synthesis_template.md` 產出最後總和彙總、舊版/新版比對、科技發展路徑判斷
19. 報告最後更新 `推播後回測與模型調整面板`

## 重要規則

- 若資料不足，必須寫「資料不足」。
- 若因果未確認，只能寫「產業訊號」或「待驗證推論」。
- 候選訊號不得因證據不足被刪除。
- 社群討論可列為潛力候選，但必須標示未證實、證據等級、原始連結、官方確認狀態或反向證據。
- 使用者指出的漏抓事件，必須進入 `memory/missed_cases.md` 的硬檢查清單。
- 跨領域事件必須標示受影響的所有雷達。
- 同一週內已播報事件需跨日去重；無新資訊不重播。
- OpenAI / Pre-IPO / Presale 類內容不得每日重複播報，除非有 volume、funding、OI、保證金、監管或交易所跟進。
- 區塊鏈段落固定包含「潛力鏈生態動向」。
- 零售段落固定升級為「零售、品牌、消費趨勢、社群媒體、流行與服飾發展」。
- 每日必須輸出固定指標追蹤總表；即使資料不足，也要標示資料缺口，不得省略。
- 每日必須輸出「科技發展與突破」段落，並分成「AI 驅動突破」與「非 AI / 單獨科技突破」。不能只寫 AI 公司或模型新聞。
- 每日必須輸出至少 5 則全球特殊應用 / 邊緣案例候選，且至少涵蓋 3 個不同領域。
- 若某雷達只抓到主流新聞或無資料，必須依 `configs/search_retry_protocol.yml` 至少換 3 種搜尋方法後，才可標示資料不足。
- 報告最後必須輸出舊版/新版補漏比對、全指標總和彙總、科技發展路徑判斷、搜尋 retry 狀態與今日最終一句話。

## 新增核心規格檔

| 檔案 | 作用 |
|---|---|
| `HIGH_LEVEL_INDEX.md` | 高階脈絡索引，避免單點回答與固定雷達遺漏 |
| `configs/indicator_tracking.yml` | 定義每日必填固定指標追蹤表，包含全球市場、加密、AI、零售、勞動與消費壓力 |
| `configs/technology_development.yml` | 定義科技發展與突破雷達。科技發展是獨立主雷達，包含 AI 驅動突破與非 AI 的單獨科技突破 |
| `configs/edge_case_discovery.yml` | 定義每日必掃全球特殊應用、非主流案例、地方試點、早期商業模式與社群弱訊號 |
| `configs/search_retry_protocol.yml` | 定義找不到資料時的每日換搜尋方法規則，至少 retry 3 種方式 |
| `templates/final_synthesis_template.md` | 定義報告最後的舊版/新版比對、全指標總和彙總、科技發展路徑判斷 |
| `AI_PROJECT_OS_ADOPTION_PLAN.md` | 本 repo 採用 AI Project OS 的升級規劃 |
| `research/README.md` | 方法論研究與公開參考的保存規範 |

## 報告索引

| 日期 | 檔案 | 本次整理內容 |
|---|---|---|
| 2026-05-30 | `reports/2026/2026-05-30.md` | 跨日去重更新版；含 BTC ETF 連續 9 日流出、台灣 GDP 上修、穩定幣微降、OpenAI pre-IPO 去重處理、社群商務與消費壓力事件簇 |
| 2026-05-31 | `reports/2026/2026-05-31.md` | 含 AI 基建、台灣 GDP、Fed／ECB 利率風險、加密 ETF 流出、pre-IPO perp、社群 AI 假內容與潛力鏈生態動向 |
| 2026-06-01 | `reports/2026/2026-06-01.md` | 新版完整架構播報；含 OpenAI pre-IPO 去重、零售品牌完整雷達、潛力鏈生態動向、台灣 GDP vs 消費信心、AI 晶片出口管制 |
| 2026-06-07 | `reports/2026/2026-06-07.md` | 含原始推播、V2.1 重做版、AI Agent／生產力便車／潛力鏈生態修正、零售品牌／商圈／百貨補洞 |
| 2026-06-08 | `reports/2026/2026-06-08.md` | 含當日推播、Strategy／STRC 漏抓反思、結構性漏抓檢查、最終推播規則整合 |
| 2026-06-26 | `reports/2026/2026-06-26.md` | 含 Seedance 2.0／AI 影片短劇產業替代漏抓回測，以及零售全域搜尋模型更新：線上 × 線下 × 整合層、百貨／購物中心、街邊店、OMO、CDP、LBS、Retail Media、AI 導購 |
| 2026-06-27 | `reports/2026/2026-06-27.md` | 新版「雷達覆蓋與證據分級」播報；含全球市場 AI 成本通膨、加密 ETF／Stablecoin／Perp DEX、企業 Agent 工作流、618 消費疲乏、氣候商品企劃、四大指標整合趨勢判斷 |

完整索引詳見：`reports/INDEX.md`

## 建議檔案命名

每日報告建議放在：

```text
reports/YYYY/YYYY-MM-DD.md
```

例如：

```text
reports/2026/2026-06-26.md
```

## 使用方式

產出每日報告前，需先讀取本 repo 的入口層、configs、memory、templates 與近期 reports。
