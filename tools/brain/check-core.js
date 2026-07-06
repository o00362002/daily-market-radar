#!/usr/bin/env node
'use strict';
/*
  check-core.js — daily-market-radar 結構體檢（不變式 4 的消費者）。
  改編自 brain-core/tools/brain/check-core.js，為 child mount 調整必備檔與記憶檔名。

  驗三件事：
    1. 必備檔存在（child mount 的最小完整性）
    2. 入口預算（P2）：AGENTS.md ≤4500、CLAUDE.md ≤1200、CURRENT_STATE 頭部 ≤8000
    3. 不變式准入（P1 半強制）：AGENTS.md「五條不變式」區塊條目數 = EXPECTED_INVARIANTS；
       想增減 → 同輪帶對應檢查器並改本檔。

  Usage: node tools/brain/check-core.js [repoDir]
  Exit:  0 = complete, 1 = 結構紅
*/
const fs = require('fs');
const path = require('path');

const repo = path.resolve(process.cwd(), process.argv[2] || path.resolve(__dirname, '..', '..'));
const EXPECTED_INVARIANTS = 5;

const REQUIRED = [
  'AGENTS.md', 'CLAUDE.md', 'README.md', 'CURRENT_STATE.md', 'CURRENT_DECISIONS.md',
  'brain.manifest.yaml', 'PROJECT_OS_MOUNT.md', 'schema/sync-matrix.json',
  'SOURCE_LIBRARY_SPEC.md', 'sources/key_media_library.yml',
  'configs/source_routing_rules.yml', 'configs/edge_case_discovery.yml', 'configs/query_recipes.yml',
  'domains/README.md', 'domains/_template/domain_pack.json', 'domains/_template/sources.json',
  'memory/potential_pool.md',
  'tools/brain/check-doc-paths.js', 'tools/brain/check-sync-matrix.js',
  'tools/brain/check-core.js', 'tools/brain/check-domain-packs.js',
  'tools/install_hooks.sh', 'check_mount_integrity.sh',
];
const BUDGETS = { 'AGENTS.md': 4500, 'CLAUDE.md': 1200 };
const STATE_HEAD_BUDGET = 8000;
const ROOT_MD_BUDGET = 22; // advisory：根目錄 md 檔數（含凍結歷史），防入口層繼續長胖

let FAIL = 0, WARN = 0;
const fail = (m) => { console.log('FAIL  ' + m); FAIL++; };
const warn = (m) => { console.log('WARN  ' + m); WARN++; };
const pass = (m) => console.log('pass  ' + m);
const rd = (f) => fs.readFileSync(path.join(repo, f), 'utf8');

console.log('daily-market-radar 結構體檢（brain-core child mount）');

// 1. 必備檔
for (const f of REQUIRED) {
  fs.existsSync(path.join(repo, f)) ? pass(f + ' 存在') : fail(f + ' 缺失');
}

// 2. 入口預算
for (const [f, cap] of Object.entries(BUDGETS)) {
  if (!fs.existsSync(path.join(repo, f))) continue;
  const n = Buffer.byteLength(rd(f), 'utf8');
  n <= cap ? pass(`${f} ${n} ≤ ${cap} 字元`) : fail(`${f} ${n} 超過預算 ${cap}——入口稅回升，先修剪再 commit`);
}
if (fs.existsSync(path.join(repo, 'CURRENT_STATE.md'))) {
  const t = rd('CURRENT_STATE.md');
  const head = t.split(/^## 歷程/m)[0];
  const n = Buffer.byteLength(head, 'utf8');
  n <= STATE_HEAD_BUDGET ? pass(`CURRENT_STATE 頭部 ${n} ≤ ${STATE_HEAD_BUDGET}`) : fail(`CURRENT_STATE 頭部 ${n} 超標——執行 P5 輪替（dated 段搬 archive/）`);
}

// 3. 不變式准入（數量鎖）
if (fs.existsSync(path.join(repo, 'AGENTS.md'))) {
  const t = rd('AGENTS.md');
  const seg = t.split(/不變式/)[1] || '';
  const block = (seg.match(/```text([\s\S]*?)```/) || [, ''])[1];
  const n = (block.match(/^\s*\d+\./gm) || []).length;
  n === EXPECTED_INVARIANTS
    ? pass(`不變式 ${n}/${EXPECTED_INVARIANTS}（增減需同輪帶檢查器並改本檔）`)
    : fail(`不變式數 ${n} ≠ ${EXPECTED_INVARIANTS}——新規則要有機器消費者：加檢查器、改 EXPECTED_INVARIANTS，同輪完成`);
}

// 4. 矩陣合法
try {
  const m = JSON.parse(rd('schema/sync-matrix.json'));
  m.schema === 'brain-sync-matrix/v1' ? pass('sync-matrix 格式合法') : fail('sync-matrix 缺 schema 標記');
} catch (e) { fail('sync-matrix JSON 壞了：' + e.message); }

// 5. 關口與體重（advisory）
fs.existsSync(path.join(repo, '.git/hooks/pre-commit'))
  ? pass('pre-commit hook 已安裝')
  : warn('hook 未安裝——bash tools/install_hooks.sh（規則不會自己出現直到你裝上它）');
try {
  const mds = fs.readdirSync(repo).filter((f) => f.endsWith('.md'));
  mds.length <= ROOT_MD_BUDGET ? pass(`根目錄 md 檔數 ${mds.length} ≤ ${ROOT_MD_BUDGET}`) : warn(`根目錄 md 檔數 ${mds.length} > ${ROOT_MD_BUDGET}——入口層在長胖，考慮輪替/歸檔`);
} catch { /* ignore */ }

console.log(`Result: FAIL=${FAIL} WARN=${WARN}`);
process.exit(FAIL > 0 ? 1 : 0);
