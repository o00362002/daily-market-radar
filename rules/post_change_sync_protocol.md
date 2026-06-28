# Post-Change Sync Protocol｜修改後連動同步規則

本 repo 採用 `Human-AI-Collaboration-Brain` 的 Post-Change Sync Protocol。

此規則是修改後檢查閘門，不是強制全文件同步。

```text
Repo level：Level 2 runtime-lite
Repo role：每日市場情報雷達，包含 configs、memory、templates、reports 與 loop checklist
```

本 repo 的 source of truth 以 SYSTEM_PROMPT.md、configs/、memory/、templates/、reports/ 為準。

---

## 1. 核心原則

```text
所有修改都要先檢查是否需要同步
只同步受影響文件
沒有下游影響時標記 No downstream sync required
有影響但尚未同步完成時標記 partial change
```

---

## 2. 修改強度

| 強度 | 適用情境 | 做法 |
|---|---|---|
| Light change | 錯字、格式、局部文字、例句補充 | 檢查即可，通常標記 `No downstream sync required` |
| Normal change | workflow、routing、README、狀態、runbook、template | 同步受影響文件 |
| Structural change | Level、module、profile、dependency、tool、runtime、schema、source of truth | 完整執行連動同步 |

---

## 3. Repo 層修改後檢查

若修改 repo level、profile、module 清單、routing、dependency、tool、workflow、schema、source of truth 或 runtime 邊界，檢查：

```text
README.md
SYSTEM_PROMPT.md 或同等 AI 指令檔
PROJECT_OS_MOUNT.md
PROJECT_MAP.md
HIGH_LEVEL_INDEX.md
CURRENT_STATE.md
CURRENT_DECISIONS.md
ADOPTION_LEVELS.md
CONTEXT_ROUTING.md
DEPENDENCY_MAP.md
docs/MAINTENANCE_GUIDE.md
```

不存在的檔案不用硬補，除非該 Level 需要。若判定不受影響，記錄：

```text
No downstream sync required
```

---

## 4. 變更類型對應

```text
改 Level → README + PROJECT_OS_MOUNT + ADOPTION_LEVELS + CURRENT_DECISIONS + DEPENDENCY_MAP
改 workflow → README + RUNBOOK / workflow docs + CHECKLIST + CONTEXT_ROUTING
改資料來源 / schema → README + data-schema / data_contracts + CHECKLIST + CONTEXT_ROUTING
改工具 / API / Actions / Apps Script → README + tools docs + RUNBOOK + CHECKLIST + CONTEXT_ROUTING
改 AI 讀取順序 → README + CONTEXT_ROUTING + CURRENT_DECISIONS
改目前狀態 → CURRENT_STATE，必要時同步 README
改決策 → CURRENT_DECISIONS，必要時同步 CURRENT_STATE / README
新增 / 改名 / 升降級 module → module README + mount/profile + routing + state + decisions + parent PROJECT_MAP
```

---

## 5. AI / 人類修改後回報格式

每次修改後，回報：

```text
Changed files:
Change type:
Impact scope:
Synced files:
No downstream sync required:
Partial change:
Next required sync:
```

---

## 6. 完成定義

```text
主要檔案已修改
受影響入口文件已同步，或已判定不受影響
受影響路由文件已同步，或已判定不受影響
受影響狀態文件已同步，或已判定不受影響
受影響決策文件已同步，或已判定不受影響
受影響依賴文件已同步，或已判定不受影響
未同步項目已明確列出
```

若沒有下游影響：

```text
No downstream sync required
```

若尚未同步完成：

```text
partial change
```
