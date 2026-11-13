import { setTimeout as sleep } from "node:timers/promises";

// Both endpoints read the current official main branch; no bundled schema fallback.
export async function fetchCursorSchema(filename, {
  fetchImpl = fetch,
  wait = sleep,
  token = process.env.GITHUB_TOKEN,
  warn = console.warn,
} = {}) {
  if (!["plugin.schema.json", "marketplace.schema.json"].includes(filename)) {
    throw new Error(`Unknown Cursor schema: ${filename}`);
  }
  const sources = [
    {
      url: `https://raw.githubusercontent.com/cursor/plugins/main/schemas/${filename}`,
      headers: { Accept: "application/json" },
    },
    {
      url: `https://api.github.com/repos/cursor/plugins/contents/schemas/${filename}?ref=main`,
      headers: {
        Accept: "application/vnd.github.raw+json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    },
  ];
  let lastFailure;
  for (const { url, headers } of sources) {
    for (let attempt = 0; attempt < 3; attempt++) {
      let response;
      try {
        response = await fetchImpl(url, {
          headers,
          signal: AbortSignal.timeout(15_000),
          // Never forward the API credential through a redirect.
          redirect: "error",
        });
      } catch {
        lastFailure = `${url}: network error or timeout`;
      }
      if (response?.ok) {
        // Invalid upstream JSON must fail validation, rather than trigger a fallback.
        return response.json();
      }
      let delay = 1_000 * 2 ** attempt;
      if (response) {
        lastFailure = `${url}: HTTP ${response.status}`;
        await response.body?.cancel();
        if (response.status !== 429 && response.status < 500) {
          throw new Error(`Failed to fetch official Cursor schema: ${lastFailure}`);
        }
        const retryAfter = response.headers.get("retry-after");
        if (retryAfter !== null) {
          const seconds = Number(retryAfter);
          const requested = Number.isFinite(seconds)
            ? seconds * 1_000
            : Date.parse(retryAfter) - Date.now();
          if (Number.isFinite(requested)) delay = Math.max(delay, requested);
        }
      }
      warn(`Schema fetch unavailable (${lastFailure}).`);
      // Switch endpoints rather than retry earlier than a long Retry-After.
      if (attempt === 2 || delay > 30_000) break;
      await wait(delay);
    }
  }
  throw new Error(`Unable to fetch a live official Cursor schema: ${lastFailure}`);
}
