# Daily Market Radar｜CURRENT_DECISIONS

本檔記錄每日播報系統的近期有效決策、已修正錯誤、停用舊邏輯與同步修改規則。

最後整理日期：2026-06-27

---

## 1. 最高優先決策

每日市場情報報告規格以 GitHub repo `o00362002/daily-market-radar` 為準。

執行前必須讀取：

1. `SYSTEM_PROMPT.md`
2. `PROJECT_MAP.md`
3. `CURRENT_STATE.md`
4. `CURRENT_DECISIONS.md`
5. `configs/`
6. `memory/`
7. `templates/`
8. `reports/`

若舊記憶、舊對話、舊報告與本 repo 衝突，以本 repo 的最新入口檔與核心規格為準。

---

## 2. 近期有效決策

### 2.1 每日播報不是新聞摘要

每日播報必須是「雷達覆蓋與證據分級型」情報系統，不得退回只列幾則新聞。

### 2.2 每日必須做三桶硬檢查

固定三桶：

1. 加密潛力市場
2. 零售通路 / 商圈 / 品牌變化
3. AI 實際應用

若任一桶沒有重大訊號，必須標示「無重大訊號 / 資料不足 / 本次未見高證據事件」，不得省略。

### 2.3 AI 段落不能只寫基建或模型新聞

AI 段落必須檢查實際應用，包括：

- 企業導入
- Agent 工作流
- 客服 / BI / 營運 / 內容工作流
- 權限治理
- 身份管理
- MCP / 工具層
- token / credit / quota / usage limit / pricing 等產品用量經濟

### 2.4 零售段落不能只寫宏觀消費

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

### 2.5 科技發展與突破是獨立主雷達

科技發展不得被併入 AI 公司新聞。每天都要檢查：

- AI 驅動突破
- 非 AI / 單獨科技突破
- 生物、物理、化學、材料、能源、機器人、半導體、醫療、製造、太空、量子等領域

若本次未見重大訊號，也要標示資料缺口或無重大變化。

### 2.6 每個主領域都要有台灣對應檢查

台灣映射不能只放在最後。每個主領域至少要標示：

- 台灣本地訊號
- 台灣產業關聯
- 台灣資料缺口
- 下一步查證
- 對使用者零售 / AI 工具化 / 加密觀察 / 職能發展的可行動提醒

### 2.7 無資料不能直接結束

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
| 核心任務 / 核心原則變更 | `SYSTEM_PROMPT.md`、`README.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |
| 新增雷達桶 | `SYSTEM_PROMPT.md`、`README.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md`、`configs/radars.yml`、`templates/daily_report_template.md`、本檔 |
| 新增跨領域觸發器 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`configs/triggers.yml`、`templates/daily_report_template.md`、本檔 |
| 新增固定指標 | `SYSTEM_PROMPT.md`、`CURRENT_STATE.md`、`configs/indicator_tracking.yml`、`templates/daily_report_template.md`、本檔 |
| 新增科技發展路徑 | `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md`、`configs/technology_development.yml`、`templates/final_synthesis_template.md`、本檔 |
| 新增漏抓案例 | `memory/missed_cases.md`、`memory/watchlist.md`、必要時同步 `configs/`、`templates/`、本檔 |
| 新增 watchlist | `memory/watchlist.md`、必要時同步 `configs/`、本檔 |
| 報告格式變更 | `templates/`、`SYSTEM_PROMPT.md`、`README.md`、`CURRENT_STATE.md`、本檔 |
| 新增每日報告 | `reports/YYYY/YYYY-MM-DD.md`、`reports/INDEX.md`、必要時更新 `CURRENT_STATE.md` |
| 舊規格停用 | `CURRENT_DECISIONS.md`、必要時移入或標註 `archive/`、必要時更新 `CURRENT_STATE.md` |
| 入口層或讀取順序變更 | `README.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md` |

若同步檢查後決定不修改某個相關檔案，必須在本檔的「本次架構調整紀錄」或新增決策紀錄中寫明原因。

---

## 4. 停用舊邏輯

以下舊邏輯不得再使用：

1. 只搜尋幾則新聞後直接摘要。
2. 只回答使用者問題的單點，不回到整套雷達系統。
3. AI 段落只寫模型、算力、IPO、估值，不寫實際應用。
4. 零售段落只寫消費數據，不查百貨、商圈、品牌、社群商務與服飾。
5. 加密段落只寫 BTC / ETH 價格，不查 ETF、Stablecoin、Perp DEX、RWA、tokenized stocks、AI agents x crypto、x402 等。
6. 科技發展只寫 AI 新聞，不查非 AI 科技突破。
7. 無資料就省略段落。
8. 沒有來源、時間、證據等級就下結論。
9. 沒有跨日去重就重複播報同一事件。
10. 使用者指出漏抓後，沒有進入 `memory/missed_cases.md` 或硬檢查清單。
11. 規則更新時只改單一檔案，沒有同步檢查入口檔、設定檔、模板與記憶檔。

---

## 5. 每次回答前的自檢問題

回答本 repo 相關問題前，需先檢查：

1. 這是報告產出、規格調整、漏抓檢討、模板調整，還是系統架構調整？
2. 是否需要讀 `SYSTEM_PROMPT.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md`、`CURRENT_DECISIONS.md`？
3. 是否涉及 `configs/`、`memory/`、`templates/`、`reports/`、`README.md` 的同步修改？
4. 是否可能與舊記憶或舊報告衝突？
5. 是否需要標示無法完整讀取或資料不足？
6. 是否有只做單點回答，而沒有回到整體雷達架構？
7. 若這次有改規則，是否已記錄同步修改或不修改原因？

---

## 6. 本次架構調整紀錄

### 2026-06-27｜入口層補強與同步規則明確化

已確認並整理：

- `PROJECT_MAP.md`
- `CURRENT_STATE.md`
- `CURRENT_DECISIONS.md`

本次調整目的：讓 GitHub 不只是文件倉庫，而是每日播報系統的可讀取專案大腦。

本次實際修改：

- 更新 `PROJECT_MAP.md`：加入規則更新同步檢查、版本優先順序、規格更新時的檔案連動。
- 更新 `CURRENT_DECISIONS.md`：補強同步修改矩陣，明確加入 `README.md`、`PROJECT_MAP.md`、`CURRENT_STATE.md` 與本檔的連動。

本次未修改：

- `SYSTEM_PROMPT.md`：原因是本次未改每日播報核心任務、雷達內容或輸出格式。
- `configs/`：原因是本次未新增或刪除雷達、觸發器、證據分級、固定指標或科技發展路徑。
- `memory/`：原因是本次不是新增漏抓案例或 watchlist。
- `templates/`：原因是本次未改報告正文格式或最終彙總格式。
- `README.md`：原因是 README 已包含核心定位與每日執行順序，本次只補強入口層內部同步規則。

---

## 7. 下次規格更新最小流程

1. 先判斷更新類型。
2. 依本檔第 3 節找出最低同步檢查檔案。
3. 逐一判斷是否需要修改。
4. 修改後在本檔新增決策紀錄。
5. 若某個應檢查檔案不修改，記錄不修改原因。
