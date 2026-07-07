# 2026-07-07 Missed Case：Technology AI Overcapture + Taiwan Crypto Fixed Sources

## Status

- 狀態：硬檢查中
- 使用者指出時間：2026-07-07
- 影響任務：Daily Push Brief / Full Daily Radar / News Search Output

---

## Case A：Technology radar 被 AI 過度佔位

### 漏抓 / 誤分事件

2026-07-07 每日推播中，`科技 / 半導體 / 能源` 段落實際上大量使用 AI 供應鏈、AI server、AI compliance agent 與能源地緣內容補位，沒有真正完成獨立的「科技發展與突破」雷達。

### 判定

這是分類錯誤，不是使用者主觀偏好。

- AI server / GPU / AI governance / AI compliance agent 應優先放入 AI / Agent / AI supply chain。
- 能源地緣 / 油價 / OPEC 產量若沒有技術突破，不得用來填 technology development quota。
- Samsung / memory cycle 可放入半導體，但若只是財報與市場預期，仍需標示為產業週期訊號，不等於科技突破。

### 修正規則

1. AI domain 禁止重複佔用 Technology domain quota。
2. Technology 段每日必須至少檢查非 AI 技術子域：半導體、機器人硬體、能源科技、量子、生技 / 醫療科技、太空 / 通訊、新材料、製造科技。
3. Daily Push Brief 若找不到非 AI 高證據科技突破，必須寫：`非 AI / 單獨科技突破：本次未見高證據重大訊號 / 資料缺口`。
4. 純市場價格、財報、能源地緣不得冒充 technology breakthrough。
5. 每則科技訊號必須標示 technology_maturity：research / prototype / benchmark / pilot / commercialization / cost_curve / supply_chain。
6. AI 驅動科技突破與非 AI / 單獨科技突破必須分段，不可混成 AI 公司新聞。

### 下次檢查關鍵字

- semiconductor breakthrough advanced packaging HBM photonics chiplet lithography
- robotics actuator humanoid robot sensor dexterity warehouse robot
- battery energy density solid state battery grid storage geothermal SMR fusion
- quantum error correction quantum sensing quantum network
- CRISPR clinical trial synthetic biology medical device breakthrough
- reusable launch satellite direct to device optical communication 6G
- perovskite graphene superconducting material advanced materials
- additive manufacturing digital twin industrial automation

---

## Case B：Taiwan crypto fixed sources 未使用卻標示台灣加密新聞不足

### 漏抓 / 誤分事件

2026-07-07 每日推播中，加密段寫「台灣新聞不足」，但未明確標示是否已檢查使用者之前指定並已加入 repo 的台灣加密來源。

### 已存在的 repo 規則

`configs/source_routing_rules.yml` 與 `memory/source_experiments.md` 已包含以下台灣加密固定來源：

- DA 交易者聯盟
- 邦妮區塊鏈
- 加密城市
- 區塊勢

而且規則已明寫：若每日報告標示「台灣加密新聞不足」，必須說明是否已檢查上述來源。未檢查時需明確寫：`Taiwan crypto fixed sources not checked.`

### 判定

這是執行錯誤。正確表述不是「台灣加密沒有來源」，而是：

```text
本輪未成功完成台灣加密固定來源檢查，因此不得宣稱台灣加密新聞不足，只能標示 Taiwan crypto fixed sources not checked / partial。
```

### 抓取可行性分級

| 來源 | 可加入固定來源庫 | 可否穩定自動抓 | 注意事項 |
|---|---:|---:|---|
| 加密城市 | yes | medium | 若有網站文章 / RSS / 搜尋結果，較容易抓。重大政策仍需官方交叉驗證。 |
| 區塊勢 | yes | medium | 適合深度分析與結構解讀。觀點不得直接寫成政策事實。 |
| 邦妮區塊鏈 | yes | low-medium | 若主要內容在社群或影音，泛搜尋可能漏抓。 |
| DA 交易者聯盟 | yes | low-medium | IG / Threads / FB 內容常不被搜尋完整索引，需 direct channel check 或使用者提供連結 / 截圖。 |

### 新增輸出要求

Crypto 台灣段若沒有新聞，必須輸出：

```text
Taiwan crypto fixed sources checked: yes / partial / no
Checked sources: DA 交易者聯盟 / 邦妮區塊鏈 / 加密城市 / 區塊勢
Official legislative trigger checked: yes / partial / no
Result: no qualified new signal / source inaccessible / not checked
```

### 新增回測規則

若本輪無法直接讀取 IG / Threads / LINE / FB：

- 不得寫「來源無資料」。
- 必須寫「social channel not directly checked」。
- 若使用者提供截圖、貼文連結或文字內容，可列為 C 級 / medium-low 候選，再交叉驗證官方或媒體來源。
