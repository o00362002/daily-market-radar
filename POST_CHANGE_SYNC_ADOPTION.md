# daily-market-radar｜Post-Change Sync Adoption

本檔說明本 repo 已採用 Brain 母架構的修改後連動同步規則。

```text
Architecture source：Human-AI-Collaboration-Brain
Rule：rules/post_change_sync_protocol.md
Level：Level 2 runtime-lite
```

## 核心用途

此規則不是要求每次全文件同步，而是要求每次修改後先檢查是否影響：

```text
README
CURRENT_STATE
CURRENT_DECISIONS
CONTEXT_ROUTING
DEPENDENCY_MAP
PROJECT_MAP
module docs
workflow docs
tool docs
schema / data contracts
```

## 負擔控制

```text
Light change → 檢查後可標記 No downstream sync required
Normal change → 同步受影響文件
Structural change → 完整執行 Post-Change Sync Protocol
```
