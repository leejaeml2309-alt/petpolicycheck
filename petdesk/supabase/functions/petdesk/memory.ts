// In-memory Store used by the local preview server and tests (mirrors 001_petdesk_starter.sql).
import type { Account, Route, Store } from "./core.ts";
export function memoryStore(): Store & { _dump(): unknown } {
  const acc = new Map<string, Account>(); const pass: any[] = []; const watch = new Map<string, string[]>(); const ev = new Set<string>();
  const byHash = (h: string) => [...acc.values()].find((a) => a.license_hash === h) ?? null;
  return {
    async getByHash(h) { return byHash(h); },
    async getById(id) { return acc.get(id) ?? null; },
    async upsert(a) {
      const cur = byHash(a.license_hash);
      const row = { ...(cur ?? { id: crypto.randomUUID(), seats: 1, agency_name: "" }), ...a } as Account;
      if (cur && cur.agency_name && !a.agency_name) row.agency_name = cur.agency_name;
      acc.set(row.id, row); return row;
    },
    async update(id, patch) { const a = acc.get(id); if (a) acc.set(id, { ...a, ...patch }); },
    async countPassports(id, period) { return pass.filter((p) => p.account_id === id && p.period === period).length; },
    async issue(id, route: Route, langs, clientRef, limit) {
      const period = new Date().toISOString().slice(0, 7);
      const used = pass.filter((p) => p.account_id === id && p.period === period).length;
      if (used >= limit) throw new Error("quota_reached");
      const ref = `PD-${period.replace("-", "")}-${id.replace(/-/g, "").slice(0, 4).toUpperCase()}-${String(used + 1).padStart(2, "0")}`;
      pass.push({ account_id: id, period, ref, route, langs, client_ref: clientRef || null, created_at: new Date().toISOString() });
      return { ref, used: used + 1, quota: limit };
    },
    async listPassports(id) { return pass.filter((p) => p.account_id === id).slice(-20).reverse().map(({ account_id, period, ...r }) => r); },
    async getPassport(id, ref) { const p = pass.find((x) => x.account_id === id && x.ref === ref); if (!p) return null; const { account_id, period, ...r } = p; return r; },
    async getWatch(id) { return watch.get(id) ?? []; },
    async setWatch(id, slugs) { watch.set(id, slugs); },
    async addEvent(r, k) { const s = r + "|" + k; if (ev.has(s)) return false; ev.add(s); return true; },
    async bySubscription(sid) { return [...acc.values()].find((a) => a.subscription_id === sid) ?? null; },
    _dump() { return { acc: [...acc.values()], pass, watch: [...watch] }; },
  };
}
