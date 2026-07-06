#!/usr/bin/env node
'use strict';
/*
  check-domain-packs.js — 領域包完整性檢查（不變式 5 的消費者）。

  規則（「多領域可擴充」的機器化保證）：
    domains/ 下每個非底線開頭的目錄＝一個領域包，必須有：
      1. domain_pack.json — schema=domain-pack/v1，必備欄位：
         id / name / positioning / scope[] / required_questions[] /
         mainstream_search_angles[] / edge_search_angles[] / output_mapping[] /
         taiwan_mapping_rule / minimum_daily{large_news, candidates}
         且不得殘留 <角括號> 佔位符。
      2. sources.json — schema=news-source-pack/v1，至少 1 個 tier（每個 tier 有 name
         ＋非空 sources[]，每個 source 有 name 且有 url/rss/query 其一），
         至少 1 條 query_recipe（每條有 id + query）。
    domains/_template/ 只驗結構存在，允許佔位符（它是複製起點）。

  這保證：新領域照 _template 填完就會被引擎完整抓到；填不完整在 commit 關口被擋。

  Usage: node tools/brain/check-domain-packs.js [repoDir]
  Exit:  0 = complete, 1 = 領域包紅
*/
const fs = require('fs');
const path = require('path');

const repo = path.resolve(process.cwd(), process.argv[2] || path.resolve(__dirname, '..', '..'));
const DIR = path.join(repo, 'domains');
const PACK_FIELDS = ['id', 'name', 'positioning', 'scope', 'required_questions',
  'mainstream_search_angles', 'edge_search_angles', 'output_mapping', 'taiwan_mapping_rule', 'minimum_daily'];

let FAIL = 0;
const fail = (m) => { console.log('FAIL  ' + m); FAIL++; };
const pass = (m) => console.log('pass  ' + m);

console.log('領域包完整性檢查');

if (!fs.existsSync(DIR)) { fail('domains/ 不存在'); process.exit(1); }

function loadJson(rel) {
  const p = path.join(repo, rel);
  if (!fs.existsSync(p)) { fail(`${rel} 缺失`); return null; }
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { fail(`${rel} JSON 壞了：${e.message}`); return null; }
}

function checkPack(name, isTemplate) {
  const before = FAIL;
  const packRel = `domains/${name}/domain_pack.json`;
  const srcRel = `domains/${name}/sources.json`;
  const pack = loadJson(packRel);
  const src = loadJson(srcRel);

  if (pack) {
    if (pack.schema !== 'domain-pack/v1') fail(`${packRel} 缺 schema=domain-pack/v1`);
    for (const f of PACK_FIELDS) {
      if (pack[f] === undefined) fail(`${packRel} 缺欄位 ${f}`);
    }
    if (pack.minimum_daily && (typeof pack.minimum_daily.large_news !== 'number' || typeof pack.minimum_daily.candidates !== 'number')) {
      fail(`${packRel} minimum_daily 需含數字欄位 large_news 與 candidates`);
    }
    if (!isTemplate && /<[^>]+>/.test(JSON.stringify(pack))) {
      fail(`${packRel} 殘留 <佔位符>——照 _template 填完再 commit`);
    }
  }

  if (src) {
    if (src.schema !== 'news-source-pack/v1') fail(`${srcRel} 缺 schema=news-source-pack/v1`);
    const tiers = Array.isArray(src.tiers) ? src.tiers : [];
    if (tiers.length < 1) fail(`${srcRel} 至少要 1 個 tier`);
    if (!isTemplate) {
      let sourceCount = 0;
      tiers.forEach((t, i) => {
        if (!t.name) fail(`${srcRel} tier[${i}] 缺 name`);
        const ss = Array.isArray(t.sources) ? t.sources : [];
        ss.forEach((s, k) => {
          sourceCount++;
          if (!s.name) fail(`${srcRel} tier[${i}].sources[${k}] 缺 name`);
          if (!s.url && !s.rss && !s.query) fail(`${srcRel} tier[${i}].sources[${k}]（${s.name || '?'}）缺 url/rss/query`);
        });
      });
      if (sourceCount < 1) fail(`${srcRel} 沒有任何來源`);
      const recipes = Array.isArray(src.query_recipes) ? src.query_recipes : [];
      if (recipes.length < 1) fail(`${srcRel} 至少要 1 條 query_recipe`);
      recipes.forEach((r, i) => { if (!r.id || !r.query) fail(`${srcRel} query_recipes[${i}] 缺 id 或 query`); });
      if (/<[^>]+>/.test(JSON.stringify(src))) fail(`${srcRel} 殘留 <佔位符>——照 _template 填完再 commit`);
    }
  }

  if (FAIL === before) pass(`domains/${name}/ 完整`);
}

checkPack('_template', true);
const packs = fs.readdirSync(DIR, { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith('_'))
  .map((d) => d.name);
console.log(packs.length ? `pass  領域包：${packs.join('、')}` : 'pass  目前無擴充領域包（六大核心領域仍在 configs/radars.yml）');
packs.forEach((p) => checkPack(p, false));

console.log(`Result: FAIL=${FAIL}`);
process.exit(FAIL > 0 ? 1 : 0);
