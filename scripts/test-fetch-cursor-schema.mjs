import assert from "node:assert/strict";
import test from "node:test";
import { fetchCursorSchema } from "./fetch-cursor-schema.mjs";

const schema = { type: "object", required: ["name"] };
const ok = () => Response.json(schema);

function fixture(responses, token = "") {
  const calls = [];
  const delays = [];
  return {
    calls,
    delays,
    options: {
      token,
      warn: () => {},
      wait: async (ms) => { delays.push(ms); },
      fetchImpl: async (url, options) => {
        calls.push({ url, ...options });
        assert.ok(options.signal instanceof AbortSignal);
        assert.equal(options.redirect, "error");
        const response = responses.shift();
        assert.ok(response, "Unexpected extra fetch");
        if (response instanceof Error) throw response;
        return response;
      },
    },
  };
}

test("retries the observed HTTP 429 and honors Retry-After", async () => {
  const f = fixture([new Response(null, { status: 429, headers: { "Retry-After": "2" } }), ok()]);
  assert.deepEqual(await fetchCursorSchema("plugin.schema.json", f.options), schema);
  assert.deepEqual(f.delays, [2_000]);
  assert.equal(f.calls[0].url, f.calls[1].url);
});

test("falls back to the live API, sending credentials only to api.github.com", async () => {
  const f = fixture([429, 429, 429].map(status => new Response(null, { status })).concat(ok()), "test-token");
  assert.deepEqual(await fetchCursorSchema("marketplace.schema.json", f.options), schema);
  assert.equal(f.calls.length, 4);
  for (const call of f.calls.slice(0, 3)) assert.equal(call.headers.Authorization, undefined);
  assert.equal(new URL(f.calls[3].url).hostname, "api.github.com");
  assert.equal(new URL(f.calls[3].url).searchParams.get("ref"), "main");
  assert.equal(f.calls[3].headers.Authorization, "Bearer test-token");
  assert.equal(f.calls[3].headers.Accept, "application/vnd.github.raw+json");
});

test("works without a token and avoids retrying before a long Retry-After", async () => {
  const f = fixture([new Response(null, { status: 429, headers: { "Retry-After": "120" } }), ok()]);
  assert.deepEqual(await fetchCursorSchema("plugin.schema.json", f.options), schema);
  assert.deepEqual(f.delays, []);
  assert.equal(f.calls[1].headers.Authorization, undefined);
});

test("retries transient network failures and server errors", async () => {
  const f = fixture([new Error("timeout"), new Response(null, { status: 503 }), ok()]);
  assert.deepEqual(await fetchCursorSchema("plugin.schema.json", f.options), schema);
  assert.deepEqual(f.delays, [1_000, 2_000]);
});

test("fails closed after bounded attempts when both official endpoints are unavailable", async () => {
  const f = fixture(Array.from({ length: 6 }, () => new Response(null, { status: 503 })));
  await assert.rejects(fetchCursorSchema("plugin.schema.json", f.options), /Unable to fetch a live official Cursor schema/);
  assert.equal(f.calls.length, 6);
  assert.deepEqual(f.delays, [1_000, 2_000, 1_000, 2_000]);
});

test("does not conceal permanent HTTP errors or malformed upstream JSON", async () => {
  for (const response of [new Response(null, { status: 404 }), new Response("invalid-json")]) {
    const f = fixture([response]);
    await assert.rejects(fetchCursorSchema("plugin.schema.json", f.options));
    assert.equal(f.calls.length, 1);
    assert.deepEqual(f.delays, []);
  }
});

test("rejects unknown schema paths before making a request", async () => {
  const f = fixture([]);
  await assert.rejects(fetchCursorSchema("../secrets", f.options), /Unknown Cursor schema/);
  assert.equal(f.calls.length, 0);
});
