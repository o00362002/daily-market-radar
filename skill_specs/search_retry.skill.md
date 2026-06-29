# Skill Spec｜search_retry

## Purpose

避免某一雷達因第一輪搜尋沒有結果、只有主流新聞、或只有低品質內容，就被寫成「無資料」。

---

## Canonical Config

```text
configs/search_retry_protocol.yml
```

---

## Trigger Conditions

任何雷達符合以下條件即觸發 retry：

```text
沒有重大訊號
只有主流大眾新聞
只有英文主流媒體
只有大公司新聞
沒有小公司 / 地方 / 研究 / 社群 / 開發者 / 試點案例
使用者指出過同類漏抓
```

---

## Minimum Retry

每個觸發雷達至少執行 3 種方法：

```text
change_keywords
change_language
change_source_type
change_level
change_time_window
search_negative_space
search_metrics_instead_of_news
```

---

## Output

```text
radar:
reason_for_retry:
retry_methods_used:
result_after_retry:
still_missing:
next_source_or_keyword:
status: resolved | partial | unresolved
```

---

## Rules

- 不得直接寫「無資料」後結束。
- 若 retry 後仍無資料，必須區分「真的無重大更新」與「搜尋仍不完整」。
- retry 過程必須寫入資料缺口或回測面板。