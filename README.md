# Daily Market Radar

這個專案是「全球每日市場情報雷達系統」的版本控管中心，不是單純存放新聞摘要。

每日播報在執行前，應先讀取本 repo 的入口層、雷達清單、固定指標追蹤、科技發展雷達、特殊應用雷達、搜尋 retry 規則、漏抓案例、歷史報告與回測規則，再進行多語言搜尋與交叉驗證。

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

## 2. Human-AI Collaboration Brain 掛載定位

本 repo 以 `Human-AI-Collaboration-Brain` 作為架構來源，採 active thin mount。

```text
Level: Level 2 Runtime-Lite Brain
Role: recurring intelligence workflow / daily report system
Mother version: v1.19-draft
Mother architecture: compact_five_layer
Mount mode: active thin mount
Layer depth: level_scaled
```

Source of truth：

```text
brain.manifest.yaml
AGENTS.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
DEPENDENCY_MAP.md
AGENT_DEFINITION_MAP.md
```

Projection files create no canonical rules. Frozen history is not current state.

---

## 3. 執行入口

AI 或協作者進入本 repo 時，先讀：

```text
SYSTEM_PROMPT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
README.md
AGENTS.md
brain.manifest.yaml
DEPENDENCY_MAP.md
AGENT_DEFINITION_MAP.md
```

再依任務讀取：

```text
configs/
memory/
templates/
reports/
workflows/
evals/
```
