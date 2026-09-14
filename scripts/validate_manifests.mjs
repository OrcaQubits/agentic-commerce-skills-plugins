#!/usr/bin/env node
/**
 * Source-manifest schema validation.
 *
 * The existing validators cover generated dist/ output; this one covers the
 * SOURCE manifests — the layer where issue #6 lived undetected for five
 * weeks. Every rule here encodes a failure class this repo actually hit:
 *
 *   #6            .claude-plugin/plugin.json `repository` as an npm-style
 *                 object fails Claude Code's manifest validation on install
 *   #6 (comment)  the Codex spec types `repository` as a string too — the
 *                 converter must not regenerate the object form into dist
 *   PR #5         hook commands invoking bare `python` fail silently on
 *                 macOS 12.3+; bare `python3` fails silently on stock
 *                 Windows (dead Store alias) — the fallback chain is load-
 *                 bearing and must not regress
 *   convert.py    plugins not registered in .claude-plugin/marketplace.json
 *                 silently ship no dist bundles
 *
 * Zero dependencies. Exits 1 on any error.
 *
 * Usage:  node scripts/validate_manifests.mjs
 */
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const warnings = [];
let passed = 0;

const ok = () => passed++;
const err = (msg) => errors.push(msg);
const warn = (msg) => warnings.push(msg);

function loadJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (e) {
    err(`${label}: invalid JSON — ${e.message}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// 1. Source Claude manifests: <plugin>/.claude-plugin/plugin.json
// ---------------------------------------------------------------------------
const pluginDirs = readdirSync(ROOT).filter((d) => {
  const p = join(ROOT, d);
  return statSync(p).isDirectory() &&
    existsSync(join(p, ".claude-plugin", "plugin.json"));
});

for (const d of pluginDirs) {
  const label = `${d}/.claude-plugin/plugin.json`;
  const j = loadJson(join(ROOT, d, ".claude-plugin", "plugin.json"), label);
  if (!j) continue;

  for (const f of ["name", "version", "description"]) {
    typeof j[f] === "string" && j[f].length
      ? ok()
      : err(`${label}: required field "${f}" missing or not a string`);
  }
  if (j.name !== d) err(`${label}: name "${j.name}" != directory "${d}"`);
  else ok();

  // Claude Code types repository as a plain URL string (issue #6).
  if ("repository" in j) {
    typeof j.repository === "string"
      ? ok()
      : err(`${label}: "repository" must be a STRING URL, got ${typeof j.repository} (issue #6)`);
  }
  if ("author" in j) {
    (typeof j.author === "object" && typeof j.author.name === "string") ||
    typeof j.author === "string"
      ? ok()
      : err(`${label}: "author" must be {name,...} or a string`);
  }
  if ("keywords" in j) {
    Array.isArray(j.keywords) && j.keywords.every((k) => typeof k === "string")
      ? ok()
      : err(`${label}: "keywords" must be an array of strings`);
  }
  if ("license" in j) {
    typeof j.license === "string" ? ok() : err(`${label}: "license" must be a string`);
  }
}

// ---------------------------------------------------------------------------
// 2. Marketplace registry ↔ plugin directories (bidirectional)
// ---------------------------------------------------------------------------
const mpPath = join(ROOT, ".claude-plugin", "marketplace.json");
const mp = loadJson(mpPath, ".claude-plugin/marketplace.json");
if (mp) {
  const registered = new Set();
  for (const p of mp.plugins || []) {
    registered.add(p.name);
    const src = join(ROOT, p.source || `./${p.name}`);
    existsSync(src)
      ? ok()
      : err(`marketplace.json: entry "${p.name}" points at missing dir ${p.source}`);
    typeof p.description === "string" && p.description.length
      ? ok()
      : err(`marketplace.json: entry "${p.name}" missing description`);
  }
  for (const d of pluginDirs) {
    registered.has(d)
      ? ok()
      : err(`plugin "${d}" is NOT registered in marketplace.json — convert.py will skip it and it will ship no dist bundles`);
  }
}

// ---------------------------------------------------------------------------
// 3. Hook commands: the python3-with-fallback chain must not regress
// ---------------------------------------------------------------------------
const FALLBACK = /^python3 .+\|\| python .+$/;
const hookFiles = [join(ROOT, "hooks.json")].filter(existsSync);
for (const d of pluginDirs) {
  const f = join(ROOT, d, "hooks", "hooks.json");
  if (existsSync(f)) hookFiles.push(f);
}
for (const f of hookFiles) {
  const label = f.slice(ROOT.length + 1).replace(/\\/g, "/");
  const j = loadJson(f, label);
  if (!j) continue;
  const commands = [];
  (function walk(o) {
    if (Array.isArray(o)) return o.forEach(walk);
    if (o && typeof o === "object") {
      if (typeof o.command === "string") commands.push(o.command);
      Object.values(o).forEach(walk);
    }
  })(j);
  for (const c of commands) {
    if (!/python/.test(c)) { ok(); continue; } // non-python hooks are fine
    FALLBACK.test(c)
      ? ok()
      : err(`${label}: python hook must use the 'python3 ... || python ...' fallback ` +
            `(bare python breaks macOS 12.3+, bare python3 breaks stock Windows): ${c.slice(0, 80)}`);
  }
}

// ---------------------------------------------------------------------------
// 4. Generated Codex manifests: repository must be a string (issue #6 pt 2)
// ---------------------------------------------------------------------------
const codexDist = join(ROOT, "dist", "codex");
if (existsSync(codexDist)) {
  for (const d of readdirSync(codexDist)) {
    const f = join(codexDist, d, ".codex-plugin", "plugin.json");
    if (!existsSync(f)) continue;
    const j = loadJson(f, `dist/codex/${d}/.codex-plugin/plugin.json`);
    if (!j) continue;
    typeof j.repository === "string" || !("repository" in j)
      ? ok()
      : err(`dist/codex/${d}: "repository" is an object — the Codex spec types it as a string; ` +
            `the converter has regressed (see scripts/converters/codex.py)`);
  }
} else {
  warn("dist/codex missing — run scripts/convert.py before validating generated output");
}

// ---------------------------------------------------------------------------
// 5. Every JSON manifest anywhere in dist parses
// ---------------------------------------------------------------------------
const distRoot = join(ROOT, "dist");
if (existsSync(distRoot)) {
  const MANIFESTS = new Set([
    "plugin.json", "marketplace.json", "package.json",
    "gemini-extension.json", "openclaw.plugin.json", "hooks.json",
  ]);
  (function walk(dir) {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (MANIFESTS.has(e.name)) {
        loadJson(p, p.slice(ROOT.length + 1).replace(/\\/g, "/")) && ok();
      }
    }
  })(distRoot);
}

// ---------------------------------------------------------------------------
console.log(`plugins: ${pluginDirs.length} · checks passed: ${passed}`);
for (const w of warnings) console.log("WARN  " + w);
for (const e of errors) console.log("ERROR " + e);
console.log(errors.length ? `\n${errors.length} error(s)` : "\nAll manifest checks passed.");
process.exit(errors.length ? 1 : 0);
