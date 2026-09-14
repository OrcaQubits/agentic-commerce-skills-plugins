#!/usr/bin/env node
/**
 * Link checker for every documentation URL referenced in the repo's markdown.
 *
 * Skills are designed to fetch live docs at invocation time. That only works if
 * the URLs they point at still resolve — a 404 in an "Official Sources" table
 * makes the fetch fail silently and the model falls back to stale static text,
 * which is exactly what the live-docs rule exists to prevent.
 *
 * Usage:
 *   node scripts/check_links.mjs              # source only (skips dist/)
 *   node scripts/check_links.mjs --all        # include generated dist/
 *   node scripts/check_links.mjs --json       # machine-readable output
 *
 * Exits non-zero if any URL returns a hard failure.
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const ARGS = new Set(process.argv.slice(2));
const INCLUDE_DIST = ARGS.has('--all');
const AS_JSON = ARGS.has('--json');

const SKIP_DIRS = new Set(['node_modules', '.git', ...(INCLUDE_DIST ? [] : ['dist'])]);

// Placeholders, private hosts, and endpoints that are not fetchable documentation.
const SKIP_URL = new RegExp([
  'example\\.', 'localhost', '127\\.0\\.0\\.1', 'your-', 'your_', 'YOUR_', 'yourdomain',
  'my-', 'myshopify', 'store-', 'site\\.com', 'merchant\\.', 'meilisearch',
  '\\.git@', '://test',
  // live API endpoints — these answer to real calls, not to GET from a checker
  'api\\.bigcommerce', 'login\\.bigcommerce', 'payments\\.bigcommerce',
  'api\\.stripe', 'api\\.openai', 'api\\.shopify', 'admin\\.shopify',
  'data-vendor', 'search-engine', 'upstream-api',
  // bot-blocked but healthy
  'npmjs\\.com', 'fidoalliance', 'cursor\\.directory', 'claude\\.ai',
  // protocol identifiers that look like URLs but are not addresses
  'ap2-protocol\\.org/extension',
].join('|'));

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP_DIRS.has(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.md')) out.push(p);
  }
  return out;
}

const files = walk(ROOT);
const seen = new Map(); // url -> Set(files)

for (const f of files) {
  const text = fs.readFileSync(f, 'utf8');
  for (const m of text.match(/https?:\/\/[A-Za-z0-9._~:/?#@!$&*+,;=%-]+/g) || []) {
    // strip trailing punctuation that belongs to the prose, not the URL
    const url = m.replace(/[).,:;`"'>\]*]+$/, '');
    if (url.length < 12 || SKIP_URL.test(url)) continue;
    if (!seen.has(url)) seen.set(url, new Set());
    seen.get(url).add(path.relative(ROOT, f).split(path.sep).join('/'));
  }
}

const urls = [...seen.keys()].sort();
if (!AS_JSON) console.error(`Checking ${urls.length} URLs across ${files.length} markdown files...`);

const CONCURRENCY = 24;
const TIMEOUT_MS = 15000;
const results = [];
let cursor = 0;

async function probe(url) {
  for (let attempt = 0; attempt < 2; attempt++) {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
    try {
      const r = await fetch(url, {
        redirect: 'follow',
        signal: ctl.signal,
        headers: { 'user-agent': 'Mozilla/5.0 (compatible; repo-link-check)' },
      });
      clearTimeout(timer);
      return { status: r.status, finalUrl: r.url };
    } catch (e) {
      clearTimeout(timer);
      if (attempt === 1) return { status: 0, error: e.message };
    }
  }
}

async function worker() {
  while (cursor < urls.length) {
    const url = urls[cursor++];
    const r = await probe(url);
    results.push({ url, ...r, files: [...seen.get(url)] });
  }
}

await Promise.all(Array.from({ length: CONCURRENCY }, worker));
results.sort((a, b) => a.url.localeCompare(b.url));

// 403/429 are usually bot protection on a healthy page, not rot — warn, don't fail.
const broken = results.filter(r => r.status === 404 || r.status === 410 || r.status >= 500 || r.status === 0);
const warned = results.filter(r => r.status === 403 || r.status === 429);
const moved = results.filter(r => r.status === 200 && r.finalUrl && r.finalUrl.replace(/\/$/, '') !== r.url.replace(/\/$/, ''));

if (AS_JSON) {
  console.log(JSON.stringify({ checked: results.length, broken, warned, moved }, null, 2));
} else {
  if (moved.length) {
    console.error(`\n${moved.length} redirected (consider updating to the final URL):`);
    for (const r of moved) console.error(`  ${r.url}\n      -> ${r.finalUrl}`);
  }
  if (warned.length) {
    console.error(`\n${warned.length} blocked by bot protection (not treated as failures):`);
    for (const r of warned) console.error(`  ${r.status}  ${r.url}`);
  }
  if (broken.length) {
    console.error(`\n${broken.length} BROKEN:`);
    for (const r of broken) {
      console.error(`  ${r.status || r.error}  ${r.url}`);
      for (const f of r.files) console.error(`        ${f}`);
    }
  }
  console.error(`\n${results.length - broken.length}/${results.length} resolve.`);
}

process.exit(broken.length ? 1 : 0);
