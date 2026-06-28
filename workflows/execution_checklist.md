# 每日執行檢查清單

每日播報前、搜尋中、輸出前、輸出後，必須依照本檢查清單執行。

---

## A. 執行前

- [ ] 讀取 `SYSTEM_PROMPT.md`
- [ ] 讀取 `PROJECT_MAP.md`
- [ ] 讀取 `HIGH_LEVEL_INDEX.md`
- [ ] 讀取 `CURRENT_STATE.md`
- [ ] 讀取 `CURRENT_DECISIONS.md`
- [ ] 讀取 `configs/radars.yml`
- [ ] 讀取 `configs/triggers.yml`
- [ ] 讀取 `configs/evidence.yml`
- [ ] 讀取 `configs/source_strategy.md`
- [ ] 讀取 `configs/indicator_tracking.yml`
- [ ] 讀取 `configs/technology_development.yml`
- [ ] 讀取 `configs/edge_case_discovery.yml`
- [ ] 讀取 `configs/search_retry_protocol.yml`
- [ ] 讀取 `memory/missed_cases.md`
- [ ] 讀取 `memory/watchlist.md`
- [ ] 讀取 `templates/daily_report_template.md`
- [ ] 讀取 `templates/final_synthesis_template.md`
- [ ] 讀取近期 `reports/` 歷史報告
- [ ] 確認台灣時間
- [ ] 計算本週週一到週日追蹤週期
- [ ] 確認本週報告序號；若不能確認，標示待覆寫

---

## B. 搜尋中

- [ ] 英文搜尋
- [ ] 繁體中文搜尋
- [ ] 簡體中文搜尋
- [ ] 視事件補日文、韓文、歐洲語系
- [ ] 從宏觀總體掃到微觀候選訊號
- [ ] 每個必掃雷達至少判斷一次狀態
- [ ] 執行跨領域觸發器檢查
- [ ] 執行固定指標追蹤：全球市場、加密、AI/Agent/產品用量經濟、零售/消費/社群、勞動與消費壓力
- [ ] 執行科技發展與突破雷達，並分開檢查「AI 驅動科技突破」與「非 AI / 單獨科技突破」
- [ ] 非 AI / 單獨科技突破至少掃描：生物、物理、化學、材料、能源、機器人硬體、半導體、醫療、製造、太空、量子、氣候科技
- [ ] 執行全球特殊應用 / 邊緣案例搜尋，至少找 5 則候選，且涵蓋至少 3 個領域
- [ ] 若某領域只找到大眾新聞或找不到內容，依 `configs/search_retry_protocol.yml` 至少換 3 種搜尋方法
- [ ] Retry 方法需至少包含部分組合：換關鍵字、換語言、換來源類型、換層級、換時間窗、查反向/失敗案例、改查指標
- [ ] 執行 Seedance 2.0 / AI 影片 / 短劇產業替代硬檢查
- [ ] 搜尋加密潛力市場三桶：RWA / tokenized stocks / AI crypto / Perp DEX / privacy / chain ecosystems
- [ ] 搜尋 AI 產品用量經濟：Codex / Claude Code / Cursor / Copilot / token / credit / quota / pricing / promo / gift / transfer
- [ ] 搜尋零售通路三桶：百貨 / 街邊 / 商圈 / 展店撤櫃 / 社群商務 / OMO / Retail Media / AI 導購
- [ ] 搜尋 AI 實際應用三桶：企業導入 / Agent / 工作流替代

---

## C. 證據與判斷

- [ ] 每個重要訊號標示證據強度
- [ ] 拆分事實、證據、推論、不確定點
- [ ] 不把相關性寫成因果
- [ ] 不把社群討論寫成已證實事實
- [ ] 社群討論若保留為潛力候選，必須附原始來源連結或來源描述、未證實標記、官方確認狀態或反向證據
- [ ] 候選訊號不得刪除
- [ ] 資料不足必須明確寫出
- [ ] 跨領域事件標示所有受影響雷達
- [ ] 科技發展事件必須說明技術本質、是否 AI 驅動、影響領域、突破指標、商業化路徑、台灣映射
- [ ] 若沒有非 AI 單獨科技突破，也必須標示「本次未見高證據重大訊號 / 資料缺口」，不得省略
- [ ] 特殊應用 / 邊緣案例必須標示來源類型、地區、證據等級、為什麼特別、為什麼可能重要、不能下的結論、下一步驗證

---

## D. 輸出前

- [ ] 產出今日雷達覆蓋表
- [ ] 產出固定指標追蹤總表；若篇幅不足，至少產出濃縮版並標示未完整
- [ ] 產出全球特殊應用 / 邊緣案例候選，至少 5 則；若篇幅不足，輸出濃縮版並標示未完整
- [ ] 產出 3～5 則今日必看訊號
- [ ] 產出候選訊號
- [ ] 產出已掃描但無重大變化
- [ ] 產出資料不足與不確定區，並標示至少嘗試過哪些 retry 方法
- [ ] 產出所有固定章節 0～22
- [ ] 產出「科技發展與突破」段落，分成 AI 驅動突破與非 AI / 單獨科技突破，不可只寫 AI 公司新聞
- [ ] 最後整合舊版 / 新版播報比對與補漏；若無法讀取舊版，明確標示無法完整比對
- [ ] 最後輸出全指標總和彙總結果
- [ ] 最後輸出科技發展路徑判斷
- [ ] 最後輸出今日最終一句話
- [ ] 結論分成已證實事實、目前推論、待驗證

---

## E. 輸出後

- [ ] 填寫推播後回測與模型調整面板
- [ ] 標示今日漏抓風險
- [ ] 比對上次漏抓案例
- [ ] 標示全球特殊應用 / 邊緣案例是否達標
- [ ] 標示搜尋 retry protocol 是否達標
- [ ] 若使用者回報漏抓，更新 `memory/missed_cases.md`
- [ ] 若新增長期追蹤題目，更新 `memory/watchlist.md`
- [ ] 若來源策略失效，更新 `configs/source_strategy.md`
- [ ] 若固定指標不足，更新 `configs/indicator_tracking.yml`
- [ ] 若科技發展雷達不足，更新 `configs/technology_development.yml`
- [ ] 若特殊應用不足，更新 `configs/edge_case_discovery.yml`
- [ ] 若找不到資料時搜尋方法不足，更新 `configs/search_retry_protocol.yml`
- [ ] 若最後總結格式不足，更新 `templates/final_synthesis_template.md`
