// deno test --allow-env index_test.ts
import { handle, pickProvider } from "./index.ts";

function assert(c: unknown, m: string) { if (!c) throw new Error(m); }
const req = (body: unknown, secret = "s3") =>
  new Request("http://x/", { method: "POST", headers: { "x-webhook-secret": secret }, body: JSON.stringify(body) });
const rec = { id: "abc", status: "pending", title: "Train trip", body: "We took the KTX with our cat." };

Deno.test("default provider is none and leaves items pending", async () => {
  Deno.env.set("WEBHOOK_SECRET", "s3");
  Deno.env.delete("MODERATION_PROVIDER");
  assert(pickProvider().name === "none", "default none");
  const r = await (await handle(req({ type: "INSERT", schema: "public", table: "posts", record: rec }))).json();
  assert(r.provider === "none" && r.status === null, JSON.stringify(r));
});

Deno.test("wrong secret is rejected", async () => {
  Deno.env.set("WEBHOOK_SECRET", "s3");
  assert((await handle(req({}, "nope"))).status === 403, "403");
});

Deno.test("openai without key falls back to none", () => {
  Deno.env.set("MODERATION_PROVIDER", "openai");
  Deno.env.delete("OPENAI_API_KEY");
  assert(pickProvider().name === "none", "fallback");
});

Deno.test("openai verdicts (mocked)", async () => {
  Deno.env.set("MODERATION_PROVIDER", "openai");
  Deno.env.set("OPENAI_API_KEY", "k");
  Deno.env.set("SUPABASE_URL", "http://db");
  Deno.env.set("SUPABASE_SERVICE_ROLE_KEY", "service");
  const patched: string[] = [];
  const orig = globalThis.fetch;
  let result = { flagged: false, categories: {} as Record<string, boolean>, category_scores: { hate: 0.01 } as Record<string, number> };
  globalThis.fetch = ((u: string | URL | Request, init?: RequestInit) => {
    const url = String(u);
    if (url.startsWith("https://api.openai.com")) return Promise.resolve(Response.json({ results: [result] }));
    patched.push(url + " " + init?.body);
    return Promise.resolve(new Response(null, { status: 204 }));
  }) as typeof fetch;
  try {
    Deno.env.set("AUTO_PUBLISH", "false");
    let r = await (await handle(req({ type: "INSERT", schema: "public", table: "posts", record: rec }))).json();
    assert(r.status === null && patched.length === 0, "clean stays pending");
    Deno.env.set("AUTO_PUBLISH", "true");
    r = await (await handle(req({ type: "INSERT", schema: "public", table: "posts", record: rec }))).json();
    assert(r.status === "published" && patched.length === 1 && patched[0].includes("status=eq.pending"), "auto publish");
    result = { flagged: true, categories: { harassment: true }, category_scores: { harassment: 0.9 } };
    r = await (await handle(req({ type: "INSERT", schema: "public", table: "comments", record: rec }))).json();
    assert(r.status === "rejected", "reject");
    result = { flagged: false, categories: {}, category_scores: { violence: 0.5 } };
    r = await (await handle(req({ type: "INSERT", schema: "public", table: "posts", record: rec }))).json();
    assert(r.status === "flagged", "borderline");
  } finally {
    globalThis.fetch = orig;
  }
});
