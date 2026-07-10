#!/usr/bin/env node
// Generate TypeScript interfaces from the checked-in web JSON schema so the TS
// types can never silently drift from the Python contract. Run with --check to
// verify the committed file matches regeneration (used in CI).
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const schemaPath = resolve(here, '../../schemas/web.schema.json');
const outPath = resolve(here, '../src/generated/web-types.ts');

const schemas = JSON.parse(readFileSync(schemaPath, 'utf8'));

const JSON_TO_TS = { string: 'string', integer: 'number', number: 'number', boolean: 'boolean' };

function tsType(prop) {
  if (prop.$ref) return prop.$ref.split('/').pop();
  if (prop.anyOf) return prop.anyOf.map(tsType).join(' | ');
  if (prop.type === 'array') return `${tsType(prop.items)}[]`;
  return JSON_TO_TS[prop.type] || 'unknown';
}

function emitInterface(name, schema) {
  const required = new Set(schema.required || []);
  const lines = [`export interface ${name} {`];
  for (const [key, prop] of Object.entries(schema.properties || {})) {
    const optional = required.has(key) ? '' : '?';
    lines.push(`  ${key}${optional}: ${tsType(prop)};`);
  }
  lines.push('}');
  return lines.join('\n');
}

const seen = new Set();
const blocks = ['// AUTO-GENERATED from schemas/web.schema.json — do not edit by hand.', ''];
for (const [name, schema] of Object.entries(schemas)) {
  for (const [defName, defSchema] of Object.entries(schema.$defs || {})) {
    if (!seen.has(defName)) {
      seen.add(defName);
      blocks.push(emitInterface(defName, defSchema), '');
    }
  }
  if (!seen.has(name)) {
    seen.add(name);
    blocks.push(emitInterface(name, schema), '');
  }
}
const output = blocks.join('\n').replace(/\n{3,}/g, '\n\n').trimEnd() + '\n';

if (process.argv.includes('--check')) {
  const current = readFileSync(outPath, 'utf8');
  if (current !== output) {
    console.error('web-types.ts is out of date; run `npm run types` to regenerate.');
    process.exit(1);
  }
  console.log('web-types.ts is in sync with schemas/web.schema.json');
} else {
  writeFileSync(outPath, output);
  console.log(`wrote ${outPath}`);
}
