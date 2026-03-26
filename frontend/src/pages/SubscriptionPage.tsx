import { useEffect, useState } from "react";
import { apiDownload, apiFetch } from "../api/client";
import { useAppSelector } from "../app/hooks";

type Plan = {
  id: string;
  name: string;
  description: string;
  price_monthly: number;
  max_listings: number;
  search_boost?: number;
};

type Tx = {
  id: string;
  amount: number;
  currency: string;
  invoice_number?: string;
  created_at?: string;
};

/** Plans, mock Stripe, invoices (Epic 5). */
export function SubscriptionPage() {
  const user = useAppSelector((s) => s.auth.user);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [invoices, setInvoices] = useState<Tx[]>([]);

  useEffect(() => {
    void (async () => {
      const rows = (await apiFetch("/subscriptions/plans")) as Plan[];
      setPlans(rows);
    })();
  }, []);

  useEffect(() => {
    if (user?.role !== "owner") return;
    void (async () => {
      try {
        const data = (await apiFetch("/subscriptions/invoices")) as { items: Tx[] };
        setInvoices(data.items);
      } catch {
        setInvoices([]);
      }
    })();
  }, [user?.role, msg]);

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

  async function downloadInvoice(id: string) {
    const blob = await apiDownload(`/subscriptions/invoices/${id}/download`);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `invoice-${id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Plans for owners</h1>
        <p className="text-gray-600">
          Free, Basic, Pro, and Featured tiers. Mock billing locally; wire Stripe for production. Higher search boost =
          more visibility (Epic 8.2).
        </p>
      </div>
      {msg && (
        <p className={`text-sm font-medium ${msg.includes("activated") ? "text-green-600" : "text-red-600"}`}>{msg}</p>
      )}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((pl) => (
          <div key={pl.id} className="p-6 rounded-2xl border border-gray-100 bg-white shadow-sm flex flex-col gap-4">
            <div>
              <h3 className="text-xl font-semibold">{pl.name}</h3>
              <p className="text-gray-600 text-sm">{pl.description}</p>
            </div>
            <p className="text-3xl font-bold text-primary">
              {pl.price_monthly <= 0 ? "Free" : `$${pl.price_monthly}`}
              {pl.price_monthly > 0 && <span className="text-lg font-normal">/mo</span>}
            </p>
            <p className="text-sm text-gray-500">Up to {pl.max_listings} listings</p>
            {typeof pl.search_boost === "number" && (
              <p className="text-xs text-gray-500">Search boost: {pl.search_boost}</p>
            )}
            {user?.role === "owner" ? (
              <button
                type="button"
                onClick={() => void subscribe(pl.id)}
                className="mt-auto py-3 rounded-xl bg-primary text-white font-semibold hover:opacity-90"
              >
                Pay with mock gateway
              </button>
            ) : (
              <p className="text-xs text-gray-500 mt-auto">Sign in as an owner to subscribe.</p>
            )}
          </div>
        ))}
      </div>

      {user?.role === "owner" && invoices.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 p-6 space-y-3">
          <h2 className="font-semibold">Invoices</h2>
          <ul className="divide-y text-sm">
            {invoices.map((inv) => (
              <li key={inv.id} className="py-2 flex flex-wrap justify-between gap-2">
                <span>
                  {inv.invoice_number ?? inv.id} · {inv.amount} {inv.currency}
                  {inv.created_at && ` · ${new Date(inv.created_at).toLocaleDateString()}`}
                </span>
                <button
                  type="button"
                  className="text-primary font-medium"
                  onClick={() => void downloadInvoice(inv.id)}
                >
                  Download
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
