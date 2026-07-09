# Daily Market Radar

這個專案是「全球每日市場情報雷達系統」的版本控管中心，不是單純存放新聞摘要。

每日播報在執行前，應先讀取本 repo 的入口層、雷達清單、固定指標追蹤、科技發展雷達、特殊應用雷達、搜尋 retry 規則、漏抓案例、歷史報告與回測規則，再進行多語言搜尋與交叉驗證。

Control links:

```text
Parent control panel: o00362002/personal-project-brain
Local source-of-truth: this repo
Agent entry: AGENTS.md
Governance posture: core depth by default; mother depth by trigger
```

---

## 1. 核心定位

- 不是新聞摘要器。
- 不是只挑幾則主觀重要新聞的編輯。
- 不是只整理主流媒體已經大量報導的大眾新聞。
- 是一套「雷達覆蓋 + 固定指標追蹤 + 全球特殊應用搜尋 + 搜尋 retry + 證據分級 + 科技發展路徑 + 回測補漏」的每日市場情報系統。

目標是同時捕捉：

```text
全球大趨勢
資金與政策變化
產業結構變化
AI 工作流替代
AI 產品用量經濟
科技發展與突破
加密與鏈上資金流
零售、品牌、消費、社群、流行與服飾訊號
全球特殊應用、非主流案例、地方試點、早期商業模式、研究原型、開發者工具與社群弱訊號
台灣產業映射
舊版 / 新版播報補漏比對
全指標總和彙總結果
```

---

## 2. Governance posture

本 repo 採 core depth 作為預設治理薄核；必要時依 parent control panel 記錄的架構深度進入 mother depth。

```text
Parent control panel: o00362002/personal-project-brain
Governance profile: o00362002/brain-core
Current mount record: brain.manifest.yaml
```

Source of truth：

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
AGENT_DEFINITION_MAP.md
DEPENDENCY_MAP.md
schema/sync-matrix.json
```

機器層（本 repo 自足）：

```text
bash tools/install_hooks.sh          # 一次性：裝上 commit 關口
bash check_mount_integrity.sh        # 體檢（CI 同入口）
node tools/brain/check-core.js .     # 結構體檢
node tools/brain/check-domain-packs.js .  # 領域包完整性
```

Projection files create no canonical rules. Evidence files do not become memory without approval. Frozen history is not current state.

---

## 3. 執行入口

AI 或協作者進入本 repo 時，第一入口是 `AGENTS.md`（按需路由，沒有必讀清單）。

依任務讀取：

```text
configs/ sources/ domains/ memory/ templates/ reports/ workflows/ evals/
```

---

## 4. 多領域擴充與潛力池

```text
六大核心領域: configs/radars.yml + sources/key_media_library.yml（canonical）
新領域: domains/<domain_id>/ 領域包（複製 _template 填完即掛上,檢查器驗完整性）
固定查詢配方: configs/query_recipes.yml（弱模型照抄執行,不自行發明查詢）
潛力池: memory/potential_pool.md（蒐集階段不預篩:新概念/新應用/新趨勢/新組合全收）
```

---

## 5. Role Boundary / Execution Boundary

Local rule:

```text
Agent owns outcome but cannot approve itself.
Workflow orders forward execution only.
Skill judges search / coverage quality when defined.
Tool operates without semantic judgement.
Loop reviews, rejects, retries, backtests, and proposes improvement.
Evidence does not become Memory without approval.
```

---

## 6. Source-library-first radar method

Search / radar collection is moving from keyword-first to source-library-first:

```text
fixed source library
→ source-scoped keyword and topic filtering
→ generic keyword fallback
→ external discovery
→ coverage audit
```

The source library is a local execution module, not a mother-brain architecture layer.

---

## 7. Backtest / Growth Control

Backtest 不只檢查新聞漏抓，也檢查專案是否需要：

```text
keep / revise / delete / archive / add / promote / demote / observe
```

新增規則、模板、workflow、skill、loop、schema 或 source module 前，先檢查能否用凍結歷史、指回 Core、降權 Projection 或刪減重複段落解決。
