// PetPolicyCheck forum: OPTIONAL automatic moderation Edge Function.
//
// Default setup does NOT need this function: every post/comment is inserted as 'pending', the database
// keyword pre-filter rejects/flags obvious abuse instantly, and the moderator bot (forum/moderate.py,
// every ~30 min) or the owner (admin.html) publishes. Deploy this only if you want an extra AI pass.
//
// Triggered by a Supabase Database Webhook (INSERT on public.posts and public.comments).
// Env (supabase secrets set ...):
//   WEBHOOK_SECRET          required: must match the "x-webhook-secret" header set on the webhook
//   MODERATION_PROVIDER     "none" (default) | "openai"
//   OPENAI_API_KEY          only for provider "openai" (model omni-moderation-latest)
//   AUTO_PUBLISH            "false" (default): clean items stay pending for the moderator bot;
//                           "true": clean items are published immediately
//   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY  injected automatically by Supabase
//
// Rules (provider openai): violence/harassment/hate/sexual/self-harm/illicit -> rejected;
// borderline scores or an external link -> flagged; clean -> published only if AUTO_PUBLISH=true.
// Only items still 'pending' are touched, so the keyword filter's decisions are never overridden.
// Politics is handled by the keyword list in the database (moderation_terms), not by this API.

type Status = "pending" | "published" | "rejected" | "flagged";
interface Verdict { status: Status | null; reason: string }
interface Provider { name: string; check(text: string): Promise<Verdict> }

const env = (k: string, d = ""): string => Deno.env.get(k) ?? d;

const REJECT_CATS = [
  "harassment", "harassment/threatening", "hate", "hate/threatening", "sexual", "sexual/minors",
  "violence", "violence/graphic", "self-harm", "self-harm/intent", "self-harm/instructions", "illicit", "illicit/violent",
];
const BORDERLINE = 0.35; // any category score above this (but not flagged by OpenAI) -> manual review
const LINK_RE = /(https?:\/\/|www\.)/i;

const noneProvider: Provider = {
  name: "none",
  check: () => Promise.resolve({ status: null, reason: "no provider: left pending for the moderator" }),
};

const openaiProvider = (key: string): Provider => ({
  name: "openai",
  async check(text: string): Promise<Verdict> {
    const r = await fetch("https://api.openai.com/v1/moderations", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ model: "omni-moderation-latest", input: text }),
    });
    if (!r.ok) return { status: null, reason: `openai error ${r.status}: left pending` };
    const data = await r.json() as {
      results: { flagged: boolean; categories: Record<string, boolean>; category_scores: Record<string, number> }[];
    };
    const res = data.results?.[0];
    if (!res) return { status: null, reason: "openai: empty result" };
    const hit = REJECT_CATS.filter((c) => res.categories?.[c]);
    if (res.flagged || hit.length) return { status: "rejected", reason: `ai:${hit.join(",") || "flagged"}` };
    const top = Object.entries(res.category_scores ?? {}).sort((a, b) => b[1] - a[1])[0];
    if (top && top[1] > BORDERLINE) return { status: "flagged", reason: `ai:borderline:${top[0]}=${top[1].toFixed(2)}` };
    if (LINK_RE.test(text)) return { status: "flagged", reason: "ai:link" };
    return env("AUTO_PUBLISH", "false") === "true"
      ? { status: "published", reason: "ai:clean" }
      : { status: null, reason: "ai:clean (AUTO_PUBLISH off): left pending" };
  },
});

export function pickProvider(): Provider {
  const want = env("MODERATION_PROVIDER", "none").toLowerCase();
  const key = env("OPENAI_API_KEY");
  if (want === "openai" && key) return openaiProvider(key);
  return noneProvider; // also when "openai" is requested without a key
}

interface WebhookPayload {
  type: "INSERT" | "UPDATE" | "DELETE";
  table: string;
  schema: string;
  record: Record<string, unknown> | null;
}

async function patch(table: string, id: string, v: Verdict): Promise<Response> {
  const url = env("SUPABASE_URL");
  const key = env("SUPABASE_SERVICE_ROLE_KEY");
  const headers: Record<string, string> = { apikey: key, "Content-Type": "application/json", Prefer: "return=minimal" };
  if (!key.startsWith("sb_")) headers["Authorization"] = `Bearer ${key}`;
  // status=eq.pending: never override a decision already taken (keyword filter, bot, admin)
  return await fetch(`${url}/rest/v1/${table}?id=eq.${encodeURIComponent(id)}&status=eq.pending`, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ status: v.status, mod_reason: v.reason.slice(0, 300), moderated_at: new Date().toISOString() }),
  });
}

export async function handle(req: Request): Promise<Response> {
  const secret = env("WEBHOOK_SECRET");
  if (!secret || req.headers.get("x-webhook-secret") !== secret) return new Response("forbidden", { status: 403 });
  let p: WebhookPayload;
  try {
    p = await req.json() as WebhookPayload;
  } catch {
    return new Response("bad json", { status: 400 });
  }
  if (p.type !== "INSERT" || p.schema !== "public" || !["posts", "comments"].includes(p.table) || !p.record) {
    return Response.json({ skipped: true });
  }
  const rec = p.record;
  if (rec.status !== "pending") return Response.json({ skipped: "not pending" });
  const text = [rec.title, rec.body, rec.breed, rec.operator, rec.route_from, rec.route_to]
    .filter((x) => typeof x === "string" && x).join("\n");
  const provider = pickProvider();
  let v: Verdict;
  try {
    v = await provider.check(text);
  } catch (e) {
    v = { status: null, reason: `provider error: ${(e as Error).message}` };
  }
  if (v.status) {
    const r = await patch(p.table, String(rec.id), v);
    if (!r.ok) return Response.json({ error: `patch failed ${r.status}` }, { status: 500 });
  }
  return Response.json({ provider: provider.name, ...v });
}

if (import.meta.main) Deno.serve(handle);
