import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

type Plan = { id: string; name: string; description: string; price_monthly: number; max_listings: number };

export function SubscriptionPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      const rows = (await apiFetch("/subscriptions/plans")) as Plan[];
      setPlans(rows);
    })();
  }, []);

  async function subscribe(planId: string) {
    setMsg(null);
    try {
      await apiFetch("/subscriptions/subscribe", {
        method: "POST",
        json: { plan_id: planId, use_mock_payment: true },
      });
      setMsg("Subscription activated (mock payment).");
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed");
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Plans for owners</h1>
        <p className="text-gray-600">Mock billing locally; wire Stripe for production.</p>
      </div>
      {msg && <p className="text-sm text-success font-medium">{msg}</p>}
      <div className="grid md:grid-cols-2 gap-6">
        {plans.map((pl) => (
          <div key={pl.id} className="p-6 rounded-2xl border border-gray-100 bg-white shadow-sm flex flex-col gap-4">
            <div>
              <h3 className="text-xl font-semibold">{pl.name}</h3>
              <p className="text-gray-600 text-sm">{pl.description}</p>
            </div>
            <p className="text-3xl font-bold text-primary">${pl.price_monthly}/mo</p>
            <p className="text-sm text-gray-500">Up to {pl.max_listings} listings</p>
            <button
              type="button"
              onClick={() => void subscribe(pl.id)}
              className="mt-auto py-3 rounded-xl bg-primary text-white font-semibold hover:opacity-90"
            >
              Pay with mock gateway
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
