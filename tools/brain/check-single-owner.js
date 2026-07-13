#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const repo = path.resolve(process.cwd(), process.argv[2] || '.');
let failCount = 0;
const fail = (message) => { console.log(`FAIL  ${message}`); failCount += 1; };
const pass = (message) => console.log(`pass  ${message}`);

function trackedFiles() {
  try {
    return cp.execSync('git ls-files', { cwd: repo, encoding: 'utf8' }).split('\n').filter(Boolean);
  } catch {
    const out = [];
    const walk = (dir) => {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        if (entry.name === '.git' || entry.name === 'node_modules') continue;
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full);
        else out.push(path.relative(repo, full));
      }
    };
    walk(repo);
    return out;
  }
}

const files = trackedFiles();
const governanceStem = /(PROJECT_MAP|DEPENDENCY_MAP|AGENT_DEFINITION_MAP|CURRENT_STATE|CURRENT_DECISIONS|CONTEXT_ROUTING|ARCHITECTURE|GOVERNANCE|ANALYSIS_GRAPH|DECISION_GRAPH|INVARIANT|SOURCE_LIBRARY_SPEC)/i;
const parallelSuffix = /(_APPEND|_v2|_new|_copy)\.(md|json|ya?ml)$/i;
const forbiddenExact = /(^|\/)(ANALYSIS_GRAPH|DECISION_GRAPH|GOVERNANCE_COPY|INVARIANTS_COPY)\.(md|json|ya?ml)$/i;
const violations = files.filter((file) => {
  const base = path.basename(file);
  return forbiddenExact.test(file) || (governanceStem.test(base) && parallelSuffix.test(base));
});

if (violations.length) {
  for (const file of violations) fail(`parallel governance carrier: ${file}`);
} else {
  pass('no deterministic parallel governance carriers');
}

for (const required of ['brain.manifest.yaml', 'AGENT_DEFINITION_MAP.md', 'SOURCE_LIBRARY_SPEC.md']) {
  fs.existsSync(path.join(repo, required)) ? pass(`${required} exists`) : fail(`${required} missing`);
}

console.log(`Result: FAIL=${failCount}`);
if (failCount) {
  console.log('partial change required');
  process.exit(1);
}
console.log('complete');
