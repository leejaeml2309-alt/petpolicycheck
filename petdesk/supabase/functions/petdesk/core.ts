// Pet Desk Starter — access logic shared by the Edge Function and the local tests.
// Verification runs HERE (server side), never in the browser:
//   browser --license key--> Edge Function --POST /v2/licenses/verify--> Gumroad
// Docs: https://gumroad.com/help/article/76-license-keys (verify API, subscription_*_at fields)

export type Account = {
  id: string; license_hash: string; license_last4: string; plan: "starter";
  gumroad_product_id: string; gumroad_sale_id?: string | null; subscription_id?: string | null;
  email?: string | null; recurrence?: string | null; sale_timestamp?: string | null;
  status: "trial" | "active" | "cancelling" | "ended" | "refunded"; access_until?: string | null;
  agency_name?: string | null; seats: number; session_nonce?: string | null;
  last_verified_at?: string | null;
};
export type Route = { from: string; to: string; state?: string; airline?: string; pet?: string; date?: string; ret?: string; retdate?: string };
export interface Store {
  getByHash(h: string): Promise<Account | null>;
  getById(id: string): Promise<Account | null>;
  upsert(a: Partial<Account> & { license_hash: string }): Promise<Account>;
  update(id: string, patch: Partial<Account>): Promise<void>;
  countPassports(id: string, period: string): Promise<number>;
  issue(id: string, route: Route, langs: string[], clientRef: string, limit: number): Promise<{ ref: string; used: number; quota: number }>;
  listPassports(id: string): Promise<Array<{ ref: string; route: Route; langs: string[]; client_ref: string | null; created_at: string }>>;
  getPassport(id: string, ref: string): Promise<{ ref: string; route: Route; langs: string[]; client_ref: string | null; created_at: string } | null>;
  getWatch(id: string): Promise<string[]>;
  setWatch(id: string, slugs: string[]): Promise<void>;
  addEvent(resource: string, key: string, payload: unknown): Promise<boolean>;
  bySubscription(subId: string): Promise<Account | null>;
}
export type Cfg = {
  productIds: string[]; verifyUrl: string; secret: string; origins: string[];
  pingSecret?: string; now?: () => Date; fetch?: typeof fetch; reverifyHours?: number;
};

// Printable passport languages that exist in the Passport engine today (passport-ui.js has ES and IT overlays).
// Add "fr" and "de" here once their overlays exist.
export const QUOTA = 15, WATCH_MAX = 5, LANGS = ["en", "es", "it"];
const enc = new TextEncoder();

export async function sha256hex(s: string) {
  const d = await crypto.subtle.digest("SHA-256", enc.encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function b64u(b: Uint8Array | string) {
  const bytes = typeof b === "string" ? enc.encode(b) : b;
  let s = ""; bytes.forEach((x) => (s += String.fromCharCode(x)));
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function unb64u(s: string) {
  s = s.replace(/-/g, "+").replace(/_/g, "/"); while (s.length % 4) s += "=";
  return new TextDecoder().decode(Uint8Array.from(atob(s), (c) => c.charCodeAt(0)));
}
async function hmac(secret: string, msg: string) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64u(new Uint8Array(await crypto.subtle.sign("HMAC", k, enc.encode(msg))));
}
function safeEq(a: string, b: string) {
  if (a.length !== b.length) return false; let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0;
}
export async function signToken(secret: string, p: { a: string; n: string; exp: number }) {
  const body = b64u(JSON.stringify(p)); return body + "." + (await hmac(secret, body));
}
export async function readToken(secret: string, t: string, now: Date) {
  const [body, sig] = (t || "").split(".");
  if (!body || !sig || !safeEq(sig, await hmac(secret, body))) return null;
  try { const p = JSON.parse(unb64u(body)); return p.exp * 1000 > now.getTime() ? p : null; } catch { return null; }
}

// Map a Gumroad verify response to an access decision.
// subscription_*_at are "the membership end date, not the cancellation requested date" (help article 76).
export function decide(p: any, now: Date) {
  if (!p) return { ok: false, status: "invalid" as const };
  if (p.refunded || p.chargebacked || p.disputed) return { ok: false, status: "refunded" as const };
  const ends = [p.subscription_ended_at, p.subscription_cancelled_at, p.subscription_failed_at].filter(Boolean).map((x: string) => new Date(x));
  if (ends.length) {
    const end = new Date(Math.min(...ends.map((d: Date) => d.getTime())));
    if (end.getTime() <= now.getTime()) return { ok: false, status: "ended" as const, access_until: end.toISOString() };
    return { ok: true, status: "cancelling" as const, access_until: end.toISOString() };
  }
  // Gumroad's trial lasts "28-31 days depending on the month" (help article 82): first calendar month = trial.
  const start = p.sale_timestamp ? new Date(p.sale_timestamp) : null;
  if (start) {
    const t = new Date(start); t.setUTCMonth(t.getUTCMonth() + 1);
    if (t.getTime() > now.getTime()) return { ok: true, status: "trial" as const, trial_ends_approx: t.toISOString() };
  }
  return { ok: true, status: "active" as const };
}

export async function gumroadVerify(cfg: Cfg, key: string) {
  const f = cfg.fetch ?? fetch;
  for (const pid of cfg.productIds) {
    const r = await f(cfg.verifyUrl, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ product_id: pid, license_key: key, increment_uses_count: "false" }),
    });
    if (r.status === 404) { await r.body?.cancel(); continue; }
    if (!r.ok) throw new Error("gumroad_unavailable");
    const j = await r.json();
    if (j && j.success && j.purchase) return j.purchase;
  }
  return null;
}

const period = (d: Date) => d.toISOString().slice(0, 7);
const clean = (s: unknown, n: number) => String(s ?? "").replace(/[\u0000-\u001f<>]/g, "").trim().slice(0, n);

function json(status: number, body: unknown, origin: string | null, cfg: Cfg) {
  const h: Record<string, string> = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
  if (origin && cfg.origins.includes(origin)) {
    h["access-control-allow-origin"] = origin; h["vary"] = "Origin";
    h["access-control-allow-headers"] = "content-type, authorization, apikey, x-client-info";
    h["access-control-allow-methods"] = "POST, OPTIONS";
  }
  return new Response(JSON.stringify(body), { status, headers: h });
}

async function summary(store: Store, a: Account, now: Date) {
  const used = await store.countPassports(a.id, period(now));
  const watch = await store.getWatch(a.id);
  const passports = await store.listPassports(a.id);
  const trialEnds = a.sale_timestamp ? (() => { const t = new Date(a.sale_timestamp!); t.setUTCMonth(t.getUTCMonth() + 1); return t.toISOString(); })() : null;
  return {
    plan: a.plan, status: a.status, access_until: a.access_until ?? null, trial_ends_approx: a.status === "trial" ? trialEnds : null,
    email_masked: a.email ? a.email.replace(/^(.).*(@.*)$/, "$1•••$2") : null, license_last4: a.license_last4,
    recurrence: a.recurrence ?? null, agency_name: a.agency_name ?? "", seats: a.seats,
    quota: { used, limit: QUOTA, period: period(now) }, watch, watch_max: WATCH_MAX, passports,
  };
}

export async function handle(req: Request, store: Store, cfg: Cfg): Promise<Response> {
  const now = cfg.now ? cfg.now() : new Date();
  const origin = req.headers.get("origin");
  const url = new URL(req.url);
  const action = url.pathname.split("/").filter(Boolean).pop() || "";
  if (req.method === "OPTIONS") { const r = json(200, {}, origin, cfg); return new Response(null, { status: 204, headers: r.headers }); }

  // Optional phase 2: Gumroad resource-subscription callbacks (form-encoded). Secret in the URL,
  // because resource-subscription posts are not signed (https://gumroad.com/ping).
  if (action === "gumroad-ping") {
    if (!cfg.pingSecret || !safeEq(url.searchParams.get("s") || "", cfg.pingSecret)) return new Response("no", { status: 403 });
    const raw = await req.text(); const f = Object.fromEntries(new URLSearchParams(raw));
    const rn = f.resource_name || "sale"; const key = f.sale_id || f.subscription_id || "";
    const fresh = await store.addEvent(rn, key + ":" + (f.cancelled_at || f.ended_at || f.restarted_at || ""), f);
    if (fresh && f.license_key) {
      // treat as trigger only: re-read from Gumroad, as Gumroad advises
      const p = await gumroadVerify(cfg, f.license_key).catch(() => null);
      const a = await store.getByHash(await sha256hex(f.license_key));
      if (a && p) { const d = decide(p, now); await store.update(a.id, { status: d.status as any, access_until: (d as any).access_until ?? null, last_verified_at: now.toISOString() }); }
    }
    return new Response("ok");
  }

  if (req.method !== "POST") return json(405, { error: "method" }, origin, cfg);
  let body: any = {}; try { body = await req.json(); } catch { /* empty */ }

  if (action === "login") {
    const key = clean(body.license_key, 64).toUpperCase();
    if (!/^[A-Z0-9]{8}-[A-Z0-9]{8}-[A-Z0-9]{8}-[A-Z0-9]{8}$/.test(key)) return json(400, { error: "bad_key_format" }, origin, cfg);
    let p: any; try { p = await gumroadVerify(cfg, key); } catch { return json(503, { error: "gumroad_unavailable" }, origin, cfg); }
    const d = decide(p, now);
    if (!d.ok) return json(403, { error: d.status, access_until: (d as any).access_until ?? null }, origin, cfg);
    const nonce = crypto.randomUUID();
    const a = await store.upsert({
      license_hash: await sha256hex(key), license_last4: key.slice(-4), plan: "starter",
      gumroad_product_id: p.product_id, gumroad_sale_id: p.sale_id ?? null, subscription_id: p.subscription_id ?? null,
      email: p.email ?? null, recurrence: p.recurrence ?? null, sale_timestamp: p.sale_timestamp ?? null,
      status: d.status as Account["status"], access_until: (d as any).access_until ?? null, seats: 1, session_nonce: nonce,
      last_verified_at: now.toISOString(),
    });
    const token = await signToken(cfg.secret, { a: a.id, n: nonce, exp: Math.floor(now.getTime() / 1000) + 12 * 3600 });
    return json(200, { token, account: await summary(store, a, now) }, origin, cfg);
  }

  // every other action needs a valid session of the single seat
  const tok = await readToken(cfg.secret, String(body.token || ""), now);
  if (!tok) return json(401, { error: "session" }, origin, cfg);
  let a = await store.getById(tok.a);
  if (!a || a.session_nonce !== tok.n) return json(401, { error: "session_replaced" }, origin, cfg);
  if (action === "logout") { await store.update(a.id, { session_nonce: null }); return json(200, { ok: true }, origin, cfg); }

  // re-check Gumroad at most every N hours, and always when a known end date has passed
  const stale = !a.last_verified_at || now.getTime() - new Date(a.last_verified_at).getTime() > (cfg.reverifyHours ?? 6) * 3600e3;
  const passedEnd = a.access_until && new Date(a.access_until).getTime() <= now.getTime();
  if (stale || passedEnd || a.status === "trial" && a.sale_timestamp && decide({ sale_timestamp: a.sale_timestamp }, now).status !== "trial") {
    const key = String(body.license_key || "");
    if (key && (await sha256hex(key.toUpperCase())) === a.license_hash) {
      const p = await gumroadVerify(cfg, key.toUpperCase()).catch(() => undefined);
      if (p !== undefined) {
        const d = decide(p, now);
        await store.update(a.id, { status: d.status as any, access_until: (d as any).access_until ?? null, last_verified_at: now.toISOString() });
        a = (await store.getById(a.id))!;
      }
    } else if (passedEnd) {
      await store.update(a.id, { status: "ended" }); a = (await store.getById(a.id))!;
    } else if (stale) {
      return json(401, { error: "reverify" }, origin, cfg); // browser re-sends the key it keeps for this session
    }
  }
  if (a.status === "ended" || a.status === "refunded") return json(403, { error: a.status, access_until: a.access_until ?? null }, origin, cfg);

  if (action === "me") return json(200, { account: await summary(store, a, now) }, origin, cfg);

  if (action === "passport") {
    const p = await store.getPassport(a.id, clean(body.ref, 40));
    if (!p) return json(404, { error: "no_passport" }, origin, cfg);
    return json(200, { passport: p, agency_name: a.agency_name ?? "" }, origin, cfg);
  }

  if (action === "profile") {
    await store.update(a.id, { agency_name: clean(body.agency_name, 80) });
    return json(200, { account: await summary(store, (await store.getById(a.id))!, now) }, origin, cfg);
  }

  if (action === "watch") {
    const slugs = Array.isArray(body.slugs) ? [...new Set(body.slugs.map((s: unknown) => clean(s, 40).toLowerCase()))] as string[] : [];
    if (slugs.length > WATCH_MAX) return json(400, { error: "watch_limit", max: WATCH_MAX }, origin, cfg);
    if (slugs.some((s) => !/^[a-z0-9-]{2,40}$/.test(s))) return json(400, { error: "bad_slug" }, origin, cfg);
    await store.setWatch(a.id, slugs);
    return json(200, { watch: slugs }, origin, cfg);
  }

  if (action === "issue") {
    const r = body.route || {};
    const route: Route = { from: clean(r.from, 40), to: clean(r.to, 40), state: clean(r.state, 40), airline: clean(r.airline, 40),
      pet: clean(r.pet, 10), date: clean(r.date, 10), ret: clean(r.ret, 10), retdate: clean(r.retdate, 10) };
    if (!route.from || !route.to) return json(400, { error: "route" }, origin, cfg);
    const langs = Array.isArray(body.langs) ? body.langs.map((x: unknown) => clean(x, 2)) : [];
    if (langs.length !== 2 || langs[0] === langs[1] || !langs.every((l: string) => LANGS.includes(l))) return json(400, { error: "langs" }, origin, cfg);
    try {
      const out = await store.issue(a.id, route, langs, clean(body.client_ref, 60), QUOTA);
      return json(200, out, origin, cfg);
    } catch (e) {
      if (String((e as Error).message).includes("quota_reached")) return json(429, { error: "quota_reached", limit: QUOTA }, origin, cfg);
      throw e;
    }
  }
  return json(404, { error: "action" }, origin, cfg);
}
