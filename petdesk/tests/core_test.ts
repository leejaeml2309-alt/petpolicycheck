// deno test -A tests/core_test.ts — exercises the real Edge Function logic with a mocked Gumroad.
import { assertEquals, assert } from "jsr:@std/assert@1";
import { handle, decide } from "../supabase/functions/petdesk/core.ts";
import { memoryStore } from "../supabase/functions/petdesk/memory.ts";
import { fixtures, mockFetch, STARTER_PID } from "./fixtures.ts";
const O = "https://petpolicycheck.com";
function setup(now = new Date()) {
  const log: string[] = []; const store = memoryStore();
  const cfg = { productIds: [STARTER_PID], verifyUrl: "mock://v", secret: "test-session-key-0123456789abcdef0123456789", origins: [O], fetch: mockFetch(fixtures(now.getTime()), log), now: () => now, pingSecret: "pp" };
  const call = async (a: string, body: unknown) => { const r = await handle(new Request(`${O}/functions/v1/petdesk/${a}`, { method: "POST", headers: { origin: O, "content-type": "application/json" }, body: JSON.stringify(body) }), store, cfg); return { s: r.status, j: await r.json(), h: r.headers }; };
  return { call, log, store, cfg };
}
const K = { trial: "TRIAL000-AAAA1111-BBBB2222-CCCC3333", active: "ACTIVE00-AAAA1111-BBBB2222-CCCC4444", cancel: "CANCEL00-AAAA1111-BBBB2222-CCCC5555", ended: "ENDED000-AAAA1111-BBBB2222-CCCC6666", failed: "FAILED00-AAAA1111-BBBB2222-CCCC7777", refund: "REFUND00-AAAA1111-BBBB2222-CCCC8888", other: "OTHERPRD-AAAA1111-BBBB2222-CCCC9999" };

Deno.test("login outcomes per subscription state", async () => {
  const { call, log } = setup();
  assertEquals((await call("login", { license_key: K.trial })).j.account.status, "trial");
  assertEquals((await call("login", { license_key: K.active })).j.account.status, "active");
  const c = await call("login", { license_key: K.cancel }); assertEquals(c.j.account.status, "cancelling"); assert(c.j.account.access_until);
  assertEquals((await call("login", { license_key: K.ended })).s, 403);
  assertEquals((await call("login", { license_key: K.failed })).s, 403);
  assertEquals((await call("login", { license_key: K.refund })).j.error, "refunded");
  assertEquals((await call("login", { license_key: K.other })).j.error, "invalid");
  assertEquals((await call("login", { license_key: "nope" })).j.error, "bad_key_format");
  assert(log.every((l) => l.includes("increment_uses_count=false")), "never burns license uses");
});
Deno.test("CORS only for allowed origin; trial date ~1 month", async () => {
  const { call } = setup(new Date("2026-11-25T00:00:00Z"));
  const r = await call("login", { license_key: K.trial });
  assertEquals(r.h.get("access-control-allow-origin"), O);
  assertEquals(r.j.account.trial_ends_approx.slice(0, 10), "2026-12-20"); // sale 5 days ago + 1 month
});
Deno.test("1 seat: a new login closes the previous session", async () => {
  const { call } = setup();
  const a = await call("login", { license_key: K.active }); const b = await call("login", { license_key: K.active });
  assertEquals((await call("me", { token: a.j.token, license_key: K.active })).j.error, "session_replaced");
  assertEquals((await call("me", { token: b.j.token, license_key: K.active })).s, 200);
  assertEquals((await call("me", { token: b.j.token + "x", license_key: K.active })).s, 401);
});
Deno.test("15 passports per month, dual language validated", async () => {
  const { call } = setup();
  const { j } = await call("login", { license_key: K.active }); const t = j.token;
  const route = { from: "US", to: "FR", pet: "dog", date: "2026-12-20" };
  assertEquals((await call("issue", { token: t, license_key: K.active, route, langs: ["en", "en"] })).j.error, "langs");
  assertEquals((await call("issue", { token: t, license_key: K.active, route, langs: ["en", "fr"] })).j.error, "langs"); // FR not printable yet
  for (let i = 1; i <= 15; i++) assertEquals((await call("issue", { token: t, license_key: K.active, route, langs: ["en", "es"] })).j.used, i);
  const over = await call("issue", { token: t, license_key: K.active, route, langs: ["en", "it"] });
  assertEquals([over.s, over.j.error], [429, "quota_reached"]);
  const me = await call("me", { token: t, license_key: K.active }); assertEquals(me.j.account.quota.used, 15);
  const ref = me.j.account.passports[0].ref;
  assertEquals((await call("passport", { token: t, license_key: K.active, ref })).s, 200);
  assertEquals((await call("passport", { token: t, license_key: K.active, ref: "PD-OTHER" })).s, 404);
});
Deno.test("watchlist max 5; agency name kept", async () => {
  const { call } = setup();
  const t = (await call("login", { license_key: K.trial })).j.token;
  assertEquals((await call("watch", { token: t, license_key: K.trial, slugs: ["delta", "united", "american", "alaska", "jetblue", "spirit"] })).j.error, "watch_limit");
  assertEquals((await call("watch", { token: t, license_key: K.trial, slugs: ["delta", "air-canada"] })).j.watch, ["delta", "air-canada"]);
  assertEquals((await call("profile", { token: t, license_key: K.trial, agency_name: "<b>Blue Sky</b>" })).j.account.agency_name, "bBlue Sky/b");
});
Deno.test("access closes when Gumroad reports the end (re-verify after 6 h)", async () => {
  const now = new Date(); const s = setup(now);
  const t = (await s.call("login", { license_key: K.active })).j.token;
  // Gumroad now reports a cancellation that ended yesterday
  (s.cfg as any).fetch = mockFetch({ [K.active]: { ...fixtures(now.getTime())[K.active], subscription_cancelled_at: new Date(now.getTime() - 86400e3).toISOString() } });
  (s.cfg as any).now = () => new Date(now.getTime() + 7 * 3600e3);
  const r = await s.call("me", { token: t, license_key: K.active }); assertEquals([r.s, r.j.error], [403, "ended"]);
});
Deno.test("decide(): failed payment in the future keeps access", () => {
  const now = new Date("2026-11-25T00:00:00Z");
  assertEquals(decide({ subscription_failed_at: "2026-11-30T00:00:00Z", sale_timestamp: "2026-09-01T00:00:00Z" }, now).status, "cancelling");
  assertEquals(decide({ chargebacked: true }, now).ok, false);
});
Deno.test("ping endpoint requires secret and dedupes", async () => {
  const s = setup(); await s.call("login", { license_key: K.active });
  const body = new URLSearchParams({ resource_name: "cancellation", subscription_id: "S1", cancelled_at: "2026-12-01", license_key: K.active }).toString();
  const mk = (q: string) => handle(new Request(`${O}/functions/v1/petdesk/gumroad-ping${q}`, { method: "POST", body }), s.store, s.cfg);
  assertEquals((await mk("")).status, 403); assertEquals((await mk("?s=pp")).status, 200); assertEquals((await mk("?s=pp")).status, 200);
  assertEquals((s.store as any)._dump().acc.length, 1);
});

Deno.test("health + fail closed without a strong session key", async () => {
  const s = setup(); const h = await s.call("health", {}); assertEquals([h.s, h.j.configured.session_key], [200, true]);
  (s.cfg as any).secret = "short";
  assertEquals((await s.call("login", { license_key: K.active })).j.error, "not_configured");
  assertEquals((await s.call("health", {})).j.configured.session_key, false);
});
