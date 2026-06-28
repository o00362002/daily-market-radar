## 2026-06-28：採用 Post-Change Sync Protocol 作為修改後連動檢查規則

### Decision

本 repo 採用：

```text
rules/post_change_sync_protocol.md
```

作為修改後連動同步規則。

### Reason

此 repo 已採用 `Human-AI-Collaboration-Brain` 架構。為避免修改後只改單點文件，導致 README、CURRENT_STATE、CURRENT_DECISIONS、CONTEXT_ROUTING、DEPENDENCY_MAP 或 module 文件未同步，將 Post-Change Sync 設為每次修改後的檢查閘門。

### Rule

```text
所有修改都要先檢查是否需要同步
只同步受影響文件
沒有下游影響時標記 No downstream sync required
有影響但尚未同步完成時標記 partial change
```

### Scope

適用於：

```text
repo level
module level
workflow
tool / provider
data contract / schema
runtime-lite
agent runtime
content / report / template
```
