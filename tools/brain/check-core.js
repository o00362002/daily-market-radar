#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const repo = path.resolve(process.cwd(), process.argv[2] || path.resolve(__dirname, '..', '..'));
const REQUIRED = [
  'AGENTS.md', 'CLAUDE.md', 'README.md', 'CURRENT_STATE.md', 'CURRENT_DECISIONS.md',
  'brain.manifest.yaml', 'schema/sync-matrix.json', 'schema/protected-files.json',
  'SOURCE_LIBRARY_SPEC.md', 'sources/key_media_library.yml',
  'configs/source_routing_rules.yml', 'configs/edge_case_discovery.yml', 'configs/query_recipes.yml',
  'config/runtime_contract.json', 'domains/README.md', 'domains/_template/domain_pack.json',
  'domains/_template/sources.json', 'memory/potential_pool.md',
  'tools/brain/check-doc-paths.js', 'tools/brain/check-sync-matrix.js',
  'tools/brain/check-core.js', 'tools/brain/check-pre-change-confirmation.js',
  'tools/brain/check-domain-packs.js', 'tools/install_hooks.sh', 'check_mount_integrity.sh'
];
const BUDGETS = { 'AGENTS.md': 4500, 'CLAUDE.md': 1200 };
const STATE_HEAD_BUDGET = 8000;
const ROOT_MD_BUDGET = 22;

let FAIL = 0, WARN = 0;
const fail = (m) => { console.log('FAIL  ' + m); FAIL++; };
const warn = (m) => { console.log('WARN  ' + m); WARN++; };
const pass = (m) => console.log('pass  ' + m);
const rd = (f) => fs.readFileSync(path.join(repo, f), 'utf8');

console.log('daily-market-radar structural check');

for (const f of REQUIRED) {
  fs.existsSync(path.join(repo, f)) ? pass(f + ' exists') : fail(f + ' missing');
}

for (const [f, cap] of Object.entries(BUDGETS)) {
  if (!fs.existsSync(path.join(repo, f))) continue;
  const n = Buffer.byteLength(rd(f), 'utf8');
  n <= cap ? pass(`${f} ${n} <= ${cap}`) : fail(`${f} ${n} exceeds ${cap}`);
}
if (fs.existsSync(path.join(repo, 'CURRENT_STATE.md'))) {
  const head = rd('CURRENT_STATE.md').split(/^## 歷程/m)[0];
  const n = Buffer.byteLength(head, 'utf8');
  n <= STATE_HEAD_BUDGET ? pass(`CURRENT_STATE head ${n} <= ${STATE_HEAD_BUDGET}`) : fail(`CURRENT_STATE head ${n} exceeds budget`);
}

const manifest = rd('brain.manifest.yaml');
const requiredMappings = [
  'governance_owner: o00362002/brain-core',
  'structural: tools/brain/check-core.js',
  'sync_review: tools/brain/check-sync-matrix.js',
  'doc_path_reality: tools/brain/check-doc-paths.js',
  'pre_change_confirmation: tools/brain/check-pre-change-confirmation.js',
  'protected_file_policy: schema/protected-files.json',
  'domain_pack_integrity: tools/brain/check-domain-packs.js'
];
for (const item of requiredMappings) {
  manifest.includes(item) ? pass('manifest mapping: ' + item) : fail('missing manifest mapping: ' + item);
}

try {
  const m = JSON.parse(rd('schema/sync-matrix.json'));
  m.schema === 'brain-sync-matrix/v1' ? pass('sync-matrix format valid') : fail('sync-matrix schema missing');
} catch (e) { fail('sync-matrix JSON invalid: ' + e.message); }

try {
  const runtime = JSON.parse(rd('config/runtime_contract.json'));
  pass(`runtime report domains derived from array: ${runtime.report_domains.length}`);
} catch (e) { fail('runtime_contract JSON invalid: ' + e.message); }

fs.existsSync(path.join(repo, '.git/hooks/pre-commit'))
  ? pass('pre-commit hook installed')
  : warn('hook not installed; run bash tools/install_hooks.sh');
try {
  const mds = fs.readdirSync(repo).filter((f) => f.endsWith('.md'));
  mds.length <= ROOT_MD_BUDGET ? pass(`root markdown ${mds.length} <= ${ROOT_MD_BUDGET}`) : warn(`root markdown ${mds.length} > ${ROOT_MD_BUDGET}`);
} catch { /* ignore */ }

console.log(`Result: FAIL=${FAIL} WARN=${WARN}`);
process.exit(FAIL > 0 ? 1 : 0);
