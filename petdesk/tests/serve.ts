// Local preview: serves ../site and mounts the real Edge Function logic (core.ts) at /fn/petdesk/*,
// with an in-memory store and the mocked Gumroad verify API.  deno run -A tests/serve.ts [port]
import { handle } from "../supabase/functions/petdesk/core.ts";
import { memoryStore } from "../supabase/functions/petdesk/memory.ts";
import { fixtures, mockFetch, STARTER_PID } from "./fixtures.ts";
const port = Number(Deno.args[0] || 8765);
const root = new URL("../../site/", import.meta.url).pathname;
const store = memoryStore(); const log: string[] = [];
const origin = `http://127.0.0.1:${port}`;
const cfg = { productIds: [STARTER_PID], verifyUrl: "mock://gumroad/v2/licenses/verify", secret: "local-preview-secret-not-for-prod",
  origins: [origin, `http://localhost:${port}`], fetch: mockFetch(fixtures(), log) };
const types: Record<string, string> = { html: "text/html; charset=utf-8", js: "text/javascript", css: "text/css", json: "application/json", svg: "image/svg+xml", png: "image/png", jpg: "image/jpeg", webp: "image/webp", woff2: "font/woff2", ico: "image/x-icon", xml: "application/xml", txt: "text/plain" };
Deno.serve({ port, hostname: "127.0.0.1" }, async (req) => {
  const u = new URL(req.url);
  if (u.pathname.startsWith("/fn/petdesk/")) return handle(req, store, cfg);
  if (u.pathname === "/fn/_log") return new Response(JSON.stringify({ log, store: store._dump() }, null, 1), { headers: { "content-type": "application/json" } });
  let p = decodeURIComponent(u.pathname); if (p.endsWith("/")) p += "index.html";
  try { const b = await Deno.readFile(root + p.slice(1)); return new Response(b, { headers: { "content-type": types[p.split(".").pop()!] || "application/octet-stream" } }); }
  catch { try { return new Response(await Deno.readFile(root + "404.html"), { status: 404, headers: { "content-type": types.html } }); } catch { return new Response("404", { status: 404 }); } }
});
