#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import vm from 'vm';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const index = JSON.parse(fs.readFileSync(path.join(root, 'site/assets/search-index.en.json'), 'utf8'));
const code = fs.readFileSync(path.join(root, 'site/assets/site-search.js'), 'utf8');

const sandbox = {
  console,
  window: {},
  globalThis: {},
  document: {
    readyState: 'complete',
    querySelectorAll: () => [],
    addEventListener: () => {}
  }
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.runInNewContext(code, sandbox);
const { search } = sandbox.PPCSearch;

const queries = [
  'Delta', 'usa mexico', 'pug cargo', 'ESA', 'rabies titer japan',
  'hotel boston', 'YVR', 'aplhis health certificate', 'emotionnal support'
];

for (const q of queries) {
  const top = search(index, q).slice(0, 3);
  console.log('\nQ:', q);
  if (!top.length) { console.log('  (no results)'); continue; }
  top.forEach((r, i) => {
    console.log(`  ${i + 1}. [${r.page.y}] ${r.page.t} → ${r.page.u}  (score=${r.score}${r.exact ? ' exact' : ''})`);
  });
}
