// Mock of Gumroad POST /v2/licenses/verify, shaped like the documented response
// (https://gumroad.com/help/article/76-license-keys). Real Gumroad is NOT called in the preview.
export const STARTER_PID = "TEST_STARTER_PRODUCT_ID==";
const day = 86400e3;
const base = (over: Record<string, unknown>) => ({
  seller_id: "TESTSELLER", product_id: STARTER_PID, product_name: "Pet Desk Starter", email: "advisor@example.com",
  price: 4900, currency: "usd", recurrence: "monthly", sale_id: "SALE-" + Math.random().toString(36).slice(2, 8),
  subscription_id: "SUB-" + Math.random().toString(36).slice(2, 8), refunded: false, disputed: false, chargebacked: false,
  subscription_ended_at: null, subscription_cancelled_at: null, subscription_failed_at: null, ...over,
});
export function fixtures(now = Date.now()) {
  const iso = (ms: number) => new Date(ms).toISOString();
  return {
    "TRIAL000-AAAA1111-BBBB2222-CCCC3333": base({ sale_timestamp: iso(now - 5 * day) }),
    "ACTIVE00-AAAA1111-BBBB2222-CCCC4444": base({ sale_timestamp: iso(now - 45 * day), email: "paid@example.com", recurrence: "yearly", price: 46800 }),
    "CANCEL00-AAAA1111-BBBB2222-CCCC5555": base({ sale_timestamp: iso(now - 40 * day), subscription_cancelled_at: iso(now + 10 * day) }),
    "ENDED000-AAAA1111-BBBB2222-CCCC6666": base({ sale_timestamp: iso(now - 70 * day), subscription_cancelled_at: iso(now - 2 * day) }),
    "FAILED00-AAAA1111-BBBB2222-CCCC7777": base({ sale_timestamp: iso(now - 70 * day), subscription_failed_at: iso(now - 1 * day) }),
    "REFUND00-AAAA1111-BBBB2222-CCCC8888": base({ sale_timestamp: iso(now - 3 * day), refunded: true }),
    "OTHERPRD-AAAA1111-BBBB2222-CCCC9999": base({ sale_timestamp: iso(now - 3 * day), product_id: "SOME_OTHER_PRODUCT==" }),
  } as Record<string, any>;
}
export function mockFetch(fx: Record<string, any>, log: string[] = []): typeof fetch {
  return (async (_u: string | URL | Request, init?: RequestInit) => {
    const f = new URLSearchParams(String(init?.body ?? ""));
    log.push(`verify product_id=${f.get("product_id")} increment_uses_count=${f.get("increment_uses_count")}`);
    const p = fx[f.get("license_key") ?? ""];
    if (!p || p.product_id !== f.get("product_id")) return new Response(JSON.stringify({ success: false, message: "That license does not exist for the provided product." }), { status: 404 });
    return new Response(JSON.stringify({ success: true, uses: 0, purchase: { ...p, license_key: f.get("license_key") } }), { status: 200 });
  }) as typeof fetch;
}
