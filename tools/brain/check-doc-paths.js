#!/usr/bin/env node
'use strict';
/*
  check-doc-paths.js — 文件路徑現實檢查（Class B）｜doc-path reality check.

  掃 md/yaml 內「看起來是 repo 相對路徑」的字串（含 code block 內——這是
  check-links.js 刻意跳過的區域），驗證該路徑實際存在。抓的是
  「文件宣稱 vs 檔案樹現實」型漂移（例：文件仍引用已改名/已移除的資料夾）。

  精準度規則（防誤報）：
    只驗「第一段是 repo 根目錄現存項目」的 token（如 tools/x.js、schema/y.json）。
    token 不存在時先補試「.md」（容許 schema/INDEX 這種省略副檔名的慣用簡稱）。
    再以「引用檔所在目錄」解析一次（模組內 docs/x.md ＝ <module>/docs/x.md）。
    跳過含占位/萬用字元的 token（<>{}*$ 等）與 URL 行。
    跳過含豁免詞的行：歷史 / 日後 / 未來 / 尚未 / 建議 / 規劃 / 子 repo /
      when added / not yet / planned / future / Do not create / path-ok
      （歷史敘述、計畫中路徑、子 repo 檔案描述不強迫存在；行內加 path-ok 可明確豁免）。
    fenced code block 的「前導行」（``` 前 3 行內）含豁免詞 → 整個 block 豁免
      （「刻意不建的未來檔」「建議 profile」這類清單整塊列示時不逐行誤報）。
    跳過 EXEMPT 目錄（archive/reports/research/outputs/examples 等歷史與產出層）
      與 CHILD_REPO_MOUNTS.md（它登記的是「子 repo 的」檔案，不屬本 repo 檔案樹）。

  Usage: node tools/brain/check-doc-paths.js [repoDir] [--staged]
         --staged 只掃 git staged 的 md/yaml（pre-commit 快速模式）
  Exit:  0 = complete, 1 = missing paths found（advisory/mandatory 由 flow profile 決定）
*/
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const args = process.argv.slice(2);
const stagedOnly = args.includes('--staged');
const repoArg = args.find((a) => !a.startsWith('--'));
const repo = path.resolve(process.cwd(), repoArg || path.resolve(__dirname, '..', '..'));

const EXEMPT = ['archive/', 'reports/', 'research/', 'outputs/', 'examples/', 'insertions/', 'node_modules/', 'CHILD_REPO_MOUNTS.md'];
const SKIP_LINE = /(https?:\/\/|歷史|日後|未來|尚未|建議|規劃|禁止|先建|不建立|空殼|子 ?repo|母腦|mother|inherit|when added|not yet|planned|future|Do not\b|path-ok)/i;
const TOKEN = /[A-Za-z0-9_.\-一-鿿]+(?:\/[A-Za-z0-9_.\-一-鿿]+)+\/?/g;

function ls(cmd) {
  return cp.execSync(cmd, { cwd: repo, encoding: 'utf8' }).split('\n').filter(Boolean);
}
let FILES = [];
try {
  FILES = stagedOnly
    ? ls('git -c core.quotePath=false diff --cached --name-only')
    : ls('git -c core.quotePath=false ls-files');
} catch { FILES = []; }
FILES = FILES.filter((f) => /\.(md|ya?ml)$/.test(f) && !EXEMPT.some((e) => f.startsWith(e)) && fs.existsSync(path.join(repo, f)));

const roots = new Set(fs.readdirSync(repo).filter((d) => !d.startsWith('.')));

let FAIL = 0, checked = 0;
console.log(`Doc-Path Reality Gate（${stagedOnly ? 'staged' : 'tracked'} md/yaml；code block 也掃）`);
for (const f of FILES) {
  const lines = fs.readFileSync(path.join(repo, f), 'utf8').split('\n');
  // fence 前導豁免：``` 開始前 3 行內含豁免詞 → 整個 code block 跳過
  let inFence = false, fenceExempt = false;
  lines.forEach((line, i) => {
    if (/^\s*```/.test(line)) {
      if (!inFence) {
        fenceExempt = lines.slice(Math.max(0, i - 3), i).some((l) => SKIP_LINE.test(l));
        inFence = true;
      } else { inFence = false; fenceExempt = false; }
      return;
    }
    if (inFence && fenceExempt) return;
    if (SKIP_LINE.test(line)) return;
    // 全形符號與常見裝飾字元換成空白，讓 token 斷得乾淨
    const clean = line.replace(/[（）「」『』｜、，。；：★├└─▶←→＋=<>{}[\]()'"`,;!？?]/g, ' ');
    for (const raw of clean.match(TOKEN) || []) {
      let t = raw.replace(/[.,;:]+$/, '');
      if (/[_-]$/.test(t) || /YYYY/.test(t)) continue;   // 檔名前綴/日期模板（xxx_、YYYY-MM-DD_...）
      const first = t.split('/')[0];
      if (!roots.has(first)) continue;                    // 錨定：第一段必須是根目錄現存項目
      if (/^\d+$/.test(first)) continue;                  // 日期樣式 2026/07/06
      // 證據/歷史/產出層＋執行期產物（generated artifacts、runtime DB）本來就來去，token 不驗
      if (['reports', 'archive', 'research', 'outputs', 'examples', 'artifacts', 'data'].includes(first)) continue;
      checked++;
      const rel = t.replace(/\/$/, '');
      const abs = path.join(repo, rel);
      // 模組內文件的相對引用（store-master/README 寫 docs/x.md ＝ store-master/docs/x.md）
      const modAbs = path.join(repo, path.dirname(f), rel);
      if (!fs.existsSync(abs) && !fs.existsSync(abs + '.md') &&
          !fs.existsSync(modAbs) && !fs.existsSync(modAbs + '.md')) {
        console.log(`FAIL  ${f}:${i + 1} 引用的路徑不存在：${t}`);
        FAIL++;
      }
    }
  });
}
console.log(`Result: files=${FILES.length} path-refs=${checked} FAIL=${FAIL}`);
if (FAIL > 0) { console.log('文件宣稱與檔案樹不一致——更新文件或在該行加 path-ok/歷史 豁免'); process.exit(1); }
console.log('complete');
