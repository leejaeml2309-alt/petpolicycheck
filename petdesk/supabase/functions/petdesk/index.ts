// Supabase Edge Function `petdesk` — deploy with:  supabase functions deploy petdesk --no-verify-jwt
// (--no-verify-jwt because the site only has the new publishable key; this function does its own
//  auth with the Gumroad license key + an HMAC session token.)
// Optional secrets (supabase secrets set ...): GUMROAD_STARTER_PRODUCT_IDS (default: the Starter id below),
//   DESK_SESSION_SECRET (default: derived from the service-role key), PETDESK_ALLOWED_ORIGINS (default: the
//   two production origins), PETDESK_PING_SECRET (no default: /gumroad-ping stays closed until it is set). SUPABASE_URL and
//   SUPABASE_SERVICE_ROLE_KEY are injected by Supabase automatically.
import { createClient } from "npm:@supabase/supabase-js@2";
import { handle, type Store } from "./core.ts";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const one = async (q: any) => { const { data, error } = await q; if (error) throw error; return data; };

const store: Store = {
  async getByHash(h) { return await one(sb.from("petdesk_accounts").select("*").eq("license_hash", h).maybeSingle()); },
  async getById(id) { return await one(sb.from("petdesk_accounts").select("*").eq("id", id).maybeSingle()); },
  async upsert(a) {
    const row = { ...a, updated_at: new Date().toISOString() } as any;
    if (!row.agency_name) delete row.agency_name; // keep the saved agency name on re-login
    return await one(sb.from("petdesk_accounts").upsert(row, { onConflict: "license_hash" }).select("*").single());
  },
  async update(id, patch) { await one(sb.from("petdesk_accounts").update({ ...patch, updated_at: new Date().toISOString() }).eq("id", id)); },
  async countPassports(id, period) {
    const { count, error } = await sb.from("petdesk_passports").select("id", { count: "exact", head: true }).eq("account_id", id).eq("period", period);
    if (error) throw error; return count ?? 0;
  },
  async issue(id, route, langs, clientRef, limit) {
    const { data, error } = await sb.rpc("petdesk_issue_passport", { p_account: id, p_route: route, p_langs: langs, p_client_ref: clientRef, p_limit: limit });
    if (error) throw new Error(error.message); return data[0];
  },
  async listPassports(id) {
    return await one(sb.from("petdesk_passports").select("ref,route,langs,client_ref,created_at").eq("account_id", id).order("created_at", { ascending: false }).limit(20));
  },
  async getPassport(id, ref) {
    return await one(sb.from("petdesk_passports").select("ref,route,langs,client_ref,created_at").eq("account_id", id).eq("ref", ref).maybeSingle());
  },
  async getWatch(id) { return (await one(sb.from("petdesk_watch").select("slug").eq("account_id", id).order("created_at"))).map((r: any) => r.slug); },
  async setWatch(id, slugs) {
    await one(sb.from("petdesk_watch").delete().eq("account_id", id));
    if (slugs.length) await one(sb.from("petdesk_watch").insert(slugs.map((slug) => ({ account_id: id, slug }))));
  },
  async addEvent(resource, key, payload) {
    const { error } = await sb.from("petdesk_gumroad_events").insert({ resource_name: resource, dedupe_key: key, payload });
    if (error && error.code === "23505") return false; if (error) throw error; return true;
  },
  async bySubscription(sid) { return await one(sb.from("petdesk_accounts").select("*").eq("subscription_id", sid).maybeSingle()); },
};

// Pet Desk Starter product on Gumroad (public id, not a secret). The secret overrides it if set.
const STARTER_PRODUCT_ID = "Qtlp1phQoytjW-w_I-h0Og==";
// Session key: DESK_SESSION_SECRET if set; otherwise derived (HMAC-SHA256) from the service-role key
// that Supabase injects server-side, so the key is never weak or missing and never leaves the server.
async function sessionKey() {
  const own = Deno.env.get("DESK_SESSION_SECRET");
  if (own && own.length >= 32) return own;
  const sr = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  if (sr.length < 32) return "";
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(sr), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode("petdesk-session-v1"));
  return Array.from(new Uint8Array(s), (b) => b.toString(16).padStart(2, "0")).join("");
}

const cfg = {
  productIds: (Deno.env.get("GUMROAD_STARTER_PRODUCT_IDS") || STARTER_PRODUCT_ID).split(",").map((s) => s.trim()).filter(Boolean),
  verifyUrl: "https://api.gumroad.com/v2/licenses/verify",
  secret: await sessionKey(),
  origins: (Deno.env.get("PETDESK_ALLOWED_ORIGINS") || "https://petpolicycheck.com,https://www.petpolicycheck.com").split(","),
  pingSecret: Deno.env.get("PETDESK_PING_SECRET") || undefined,
};

Deno.serve(async (req) => {
  try { return await handle(req, store, cfg); }
  catch (e) { console.error(e); return new Response(JSON.stringify({ error: "server" }), { status: 500, headers: { "content-type": "application/json" } }); }
});
