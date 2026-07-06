#!/usr/bin/env node
'use strict';
/*
  check-sync-matrix.js — 連動同步「commit 時提醒」gate（sync_matrix 檢查 id 的實作）。

  與既有工具的分工（一份矩陣、兩個消費者——不重複造輪）：
    schema/sync-matrix.json        唯一矩陣（byFile 精確檔＋byPrefix 目錄前綴）
    tools/brain/sync-impact.js     查詢工具：你說改了什麼，它算出要同步什麼（事前規劃用）
    tools/brain/check-sync-matrix.js（本檔）gate：讀 staged 檔案，對「應檢視而本次未動」
                                   的檔案在 commit 時印提醒（事中把關用）

  這是提醒（advisory 起步）不是強制勾選：清單科學——固定暫停點＋短清單，
  防 checkbox fatigue。散文權威仍是 rules/post_change_sync_protocol.md。

  自足設計：零依賴、不 require lib.js——子 repo 掛載時可單檔複製，搭配子 repo
  自己的 schema/sync-matrix.json（同格式，內容依該 repo 檔名）。

  Usage: node tools/brain/check-sync-matrix.js [repoDir] [--list]
  Exit:  0 = 無提醒（或無 staged / 無矩陣）；1 = 有應檢視而未動的檔案
         （advisory/mandatory 由 flow profile／hook 決定要不要擋）
*/
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const args = process.argv.slice(2);
const repoArg = args.find((a) => !a.startsWith('--'));
const repo = path.resolve(process.cwd(), repoArg || path.resolve(__dirname, '..', '..'));
const matrixPath = path.join(repo, 'schema', 'sync-matrix.json');

console.log('Sync-Matrix Reminder Gate');
if (!fs.existsSync(matrixPath)) {
  console.log('note  此 repo 沒有 schema/sync-matrix.json——依 rules/post_change_sync_protocol.md 人工判斷');
  console.log('complete');
  process.exit(0);
}
let m;
try { m = JSON.parse(fs.readFileSync(matrixPath, 'utf8')); }
catch (e) { console.log('FAIL  schema/sync-matrix.json 不是合法 JSON：' + e.message); process.exit(1); }
const byFile = m.byFile || {};
const byPrefix = m.byPrefix || {};

if (args.includes('--list')) {
  Object.entries(byPrefix).filter(([k]) => !k.startsWith('_')).forEach(([k, v]) =>
    console.log(`  動 ${k}* → 檢視 ${v.join('、')}`));
  Object.entries(byFile).forEach(([k, v]) => console.log(`  動 ${k} → 檢視 ${v.join('、')}`));
  process.exit(0);
}

let staged = [];
try {
  staged = cp.execSync('git -c core.quotePath=false diff --cached --name-only', { cwd: repo, encoding: 'utf8' })
    .split('\n').filter(Boolean);
} catch { /* not a git repo */ }
if (!staged.length) { console.log('note  無 staged 檔案，無事可提醒'); console.log('complete'); process.exit(0); }

// staged 檔案 → 應檢視集合（byFile 精確 + byPrefix 前綴）
const need = new Map(); // review file -> [trigger files]
for (const f of staged) {
  const deps = [...(byFile[f] || [])];
  for (const [pre, list] of Object.entries(byPrefix)) {
    if (!pre.startsWith('_') && f.startsWith(pre)) deps.push(...list);
  }
  for (const d of deps) {
    if (staged.includes(d) || d === f) continue; // 已一起動了 / 自身
    if (!need.has(d)) need.set(d, []);
    need.get(d).push(f);
  }
}

console.log(`Result: staged=${staged.length} reminders=${need.size}`);
if (need.size) {
  for (const [d, trig] of need) {
    console.log(`提醒  應檢視：${d}（因為動了 ${trig[0]}${trig.length > 1 ? ` 等 ${trig.length} 檔` : ''}）${fs.existsSync(path.join(repo, d)) ? '' : '［檔案不存在——矩陣可能過時］'}`);
  }
  console.log('確認過無需同步就直接 commit（advisory 不擋）；需要同步就補完再 commit');
  process.exit(1);
}
console.log('complete');
