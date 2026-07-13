#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const repo = path.resolve(process.cwd(), process.argv[2] || path.resolve(__dirname, '..', '..'));
const policyPath = path.join(repo, 'schema/protected-files.json');
let FAIL = 0;
const fail = (m) => { console.log('FAIL  ' + m); FAIL++; };
const pass = (m) => console.log('pass  ' + m);
const warn = (m) => console.log('WARN  ' + m);

function git(args) {
  try { return cp.execFileSync('git', args, { cwd: repo, encoding: 'utf8' }).trim(); }
  catch { return ''; }
}
function isProtected(file, policy) {
  if ((policy.exempt_prefixes || []).some((p) => file.startsWith(p))) return false;
  if ((policy.protected_files || []).includes(file)) return true;
  return (policy.protected_prefixes || []).some((p) => file.startsWith(p));
}

if (!fs.existsSync(policyPath)) {
  fail('missing schema/protected-files.json');
  process.exit(1);
}

let policy;
try { policy = JSON.parse(fs.readFileSync(policyPath, 'utf8')); }
catch (e) { fail('protected-files policy JSON invalid: ' + e.message); process.exit(1); }

const staged = git(['diff', '--cached', '--name-only']).split('\n').map((s) => s.trim()).filter(Boolean);
if (staged.length === 0) {
  pass('no staged files; pre-change confirmation not applicable');
  process.exit(0);
}

const protectedChanged = staged.filter((f) => isProtected(f, policy));
if (protectedChanged.length === 0) {
  pass('no protected files staged');
  process.exit(0);
}

const confirmationDir = policy.confirmation_dir || 'reports/change-confirmations/';
const records = staged.filter((f) => f.startsWith(confirmationDir) && f.endsWith('.md'));
if (records.length === 0) {
  fail('protected files staged without a same-change confirmation record');
  for (const f of protectedChanged) console.log('  - ' + f);
  process.exit(1);
}

const required = policy.required_record_fields || [];
let anyValid = false;
for (const rec of records) {
  const abs = path.join(repo, rec);
  if (!fs.existsSync(abs)) { warn(rec + ' staged but not readable'); continue; }
  const text = fs.readFileSync(abs, 'utf8');
  const missing = required.filter((field) => !text.includes(field));
  if (missing.length === 0) {
    anyValid = true;
    pass('valid change confirmation record: ' + rec);
    break;
  }
  warn(rec + ' missing fields: ' + missing.join(', '));
}
if (!anyValid) fail('no valid change confirmation record for protected-file change');
process.exit(FAIL > 0 ? 1 : 0);
