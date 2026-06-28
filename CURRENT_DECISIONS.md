# Daily Market Radar｜CURRENT_DECISIONS

本檔記錄每日播報系統的近期有效決策、已修正錯誤、停用舊邏輯與同步修改規則。

最後整理日期：2026-06-28

---

## 1. 最高優先決策

每日市場情報報告規格以 GitHub repo `o00362002/daily-market-radar` 為準。

執行前必須讀取：

1. `SYSTEM_PROMPT.md`
2. `PROJECT_MAP.md`
3. `HIGH_LEVEL_INDEX.md`
4. `CURRENT_STATE.md`
5. `CURRENT_DECISIONS.md`
6. `ADOPTION_LEVELS.md`
7. `configs/`
8. `memory/`
9. `templates/`
10. `reports/`

若舊記憶、舊對話、舊報告與本 repo 衝突，以本 repo 的最新入口檔與核心規格為準。

---

## 2. 近期有效決策

### 2.1 本 repo 維持 Repo Level 2

本 repo 指定為：

```text
Repo Level 2：Long-term AI Project
```

每日市場雷達是長期情報系統，重點是穩定入口層、固定雷達、記憶、模板、報告與回測，不預設升級為 Agent / Product System。

若未來新增 radar module、搜尋 retry module 或回測 module，應先用 Module Level 管理，不直接把整個 repo 升級到 Level 3。

### 2.2 每日播報不是新聞摘要

每日播報必須是「雷達覆蓋與證據分級型」情報系統，不得退回只列幾則新聞。

### 2.3 HIGH_LEVEL_INDEX 納入固定入口層

`HIGH_LEVEL_INDEX.md` 是每日市場情報系統的高階脈絡索引，用來避免單點回答、漏掉固定雷達、漏掉三桶硬檢查或引用舊邏輯。

之後涉及雷達分類、固定指標、科技突破、漏抓案例、台灣映射、報告格式或 AI Project OS 架構調整時，都需要判斷是否同步更新 `HIGH_LEVEL_INDEX.md`。

### 2.4 每日必須做三桶硬檢查

固定三桶：

1. 加密潛力市場
2. 零售通路 / 商圈 / 品牌變化
3. AI 實際應用

若任一桶沒有重大訊號，必須標示「無重大訊號 / 資料不足 / 本次未見高證據事件」，不得省略。

### 2.5 AI 段落不能只寫基建或模型新聞

AI 段落必須檢查實際應用，包括：

- 企業導入
- Agent 工作流
- 客服 / BI / 營運 / 內容工作流
- 權限治理
- 身份管理
- MCP / 工具層
- token / credit / quota / usage limit / pricing 等產品用量經濟

### 2.6 零售段落不能只寫宏觀消費

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

### 2.7 科技發展與突破是獨立主雷達

科技發展不得被併入 AI 公司新聞。每天都要檢查科技發展與突破，並區分 AI 驅動與非 AI 單獨突破。
