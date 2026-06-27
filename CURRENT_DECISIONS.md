# Daily Market Radar｜CURRENT_DECISIONS

本檔記錄每日播報系統的近期有效決策、已修正錯誤、停用舊邏輯與同步修改規則。

最後整理日期：2026-06-27

---

## 1. 最高優先決策

每日市場情報報告規格以 GitHub repo `o00362002/daily-market-radar` 為準。

執行前必須讀取：

1. `SYSTEM_PROMPT.md`
2. `PROJECT_MAP.md`
3. `HIGH_LEVEL_INDEX.md`
4. `CURRENT_STATE.md`
5. `CURRENT_DECISIONS.md`
6. `configs/`
7. `memory/`
8. `templates/`
9. `reports/`

若舊記憶、舊對話、舊報告與本 repo 衝突，以本 repo 的最新入口檔與核心規格為準。

---

## 2. 近期有效決策

### 2.1 每日播報不是新聞摘要

每日播報必須是「雷達覆蓋與證據分級型」情報系統，不得退回只列幾則新聞。

### 2.2 HIGH_LEVEL_INDEX 納入固定入口層

`HIGH_LEVEL_INDEX.md` 是每日市場情報系統的高階脈絡索引，用來避免單點回答、漏掉固定雷達、漏掉三桶硬檢查或引用舊邏輯。

之後涉及雷達分類、固定指標、科技突破、漏抓案例、台灣映射、報告格式或 AI Project OS 架構調整時，都需要判斷是否同步更新 `HIGH_LEVEL_INDEX.md`。

### 2.3 每日必須做三桶硬檢查

固定三桶：

1. 加密潛力市場
2. 零售通路 / 商圈 / 品牌變化
3. AI 實際應用

若任一桶沒有重大訊號，必須標示「無重大訊號 / 資料不足 / 本次未見高證據事件」，不得省略。

### 2.4 AI 段落不能只寫基建或模型新聞

AI 段落必須檢查實際應用，包括：

- 企業導入
- Agent 工作流
- 客服 / BI / 營運 / 內容工作流
- 權限治理
- 身份管理
- MCP / 工具層
- token / credit / quota / usage limit / pricing 等產品用量經濟

### 2.5 零售段落不能只寫宏觀消費

零售段落必須包含：

- 百貨 / 購物中心
- 街邊店 / 高街
- 品牌展店 / 收店
- 商圈洗牌
- tenant mix
- OMO / CDP / CRM / LBS
- Retail Media
- AI 導購
- 社群商務
- 流行與服飾趨勢

### 2.6 科技發展與突破是獨立主雷達

科技發展不得被併入 AI 公司新聞。每天都要檢查：

- AI 驅動突破
- 非 AI / 單獨科技突破
- 生物、物理、化學、材料、能源、機器人、半導體、醫療、製造、太空、量子等領域

若本次未見重大訊號，也要標示資料缺口或無重大變化。

### 2.7 每個主領域都要有台灣對應檢查

台灣映射不能只放在最後。每個主領域至少要標示：

- 台灣本地訊號
- 台灣產業關聯
- 台灣資料缺口
- 下一步查證
- 對使用者零售 / AI 工具化 / 加密觀察 / 職能發展的可行動提醒

### 2.8 無資料不能直接結束

若某桶或某指標無資料，必須說明下一次如何降低無資料機率，例如：

- 擴大同義詞
- 增加英文 / 中文 / 區域語言關鍵字
- 改查官方資料、統計資料、財報、平台公告
- 延長到 7 日事件簇
- 交叉查新聞、官方公告、鏈上資料、社群、研究報告、GitHub、交易所公告等

---

## 3. 規則更新同步決策

之後任何規則更新，都必須判斷是否同步修改以下檔案，不能只改單一檔案：

| 更新類型 | 至少同步檢查 |
|---|---|
| 核心任務 / 核心原則變更 | `SYSTEM_PROMPT.md`、`README.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |
| 新增雷達桶 | `SYSTEM_PROMPT.md`、`README.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`configs/radars.yml`、`templates/daily_report_template.md`、本檔 |
| 新增跨領域觸發器 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`configs/triggers.yml`、`templates/daily_report_template.md`、本檔 |
| 新增固定指標 | `SYSTEM_PROMPT.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`configs/indicator_tracking.yml`、`templates/daily_report_template.md`、本檔 |
| 新增科技發展路徑 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`configs/technology_development.yml`、`templates/final_synthesis_template.md`、本檔 |
| 新增漏抓案例 | `memory/missed_cases.md`、`memory/watchlist.md`、必要時同步 `HIGH_LEVEL_INDEX.md`、`configs/`、`templates/`、本檔 |
| 新增 watchlist | `memory/watchlist.md`、必要時同步 `HIGH_LEVEL_INDEX.md`、`configs/`、本檔 |
| 報告格式變更 | `templates/`、`SYSTEM_PROMPT.md`、`README.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、本檔 |
| 新增每日報告 | `reports/YYYY/YYYY-MM-DD.md`、`reports/INDEX.md`、必要時更新 `CURRENT_STATE.md` |
| 舊規格停用 | `CURRENT_DECISIONS.md`、必要時移入或標註 `archive/`、必要時更新 `CURRENT_STATE.md`、`HIGH_LEVEL_INDEX.md` |
| 入口層或讀取順序變更 | `README.md`、`PROJECT_MAP.md`、`HIGH_LEVEL_INDEX.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |
| 方法論研究採納 | `research/`、`CURRENT_DECISIONS.md`、必要時同步 `SYSTEM_PROMPT.md`、`configs/`、`templates/`、`HIGH_LEVEL_INDEX.md` |

---

## 4. AI Project OS 採用決策

本 repo 採用 `Reference-Implementation-of-AI-Project-Operating-System` 的核心入口層：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
```

`research/` 作為方法論研究與公開參考層，不直接覆蓋正式規則。研究內容必須經過設計決策後，才同步到核心規格。