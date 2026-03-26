import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { apiFetch } from "../api/client";
import type { Property } from "../slices/propertiesSlice";

type Summary = {
  users_total: number;
  listings_pending: number;
  listings_approved: number;
  revenue_completed_total: number;
};

/** Admin analytics + sortable-style pending table with approve/reject. */
export function AdminDashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [cityRows, setCityRows] = useState<{ city: string; count: number }[]>([]);
  const [pending, setPending] = useState<Property[]>([]);
  const [reason, setReason] = useState("");

  async function refresh() {
    const s = (await apiFetch("/analytics/summary")) as Summary;
    const c = (await apiFetch("/analytics/listings-by-city")) as { city: string; count: number }[];
    const p = (await apiFetch("/admin/properties/pending")) as { items: Property[] };
    setSummary(s);
    setCityRows(c);
    setPending(p.items);
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function moderate(id: string, status: "approved" | "rejected") {
    await apiFetch(`/admin/properties/${id}/moderate`, {
      method: "POST",
      json: { status, reason: reason || undefined },
    });
    await refresh();
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Admin</h1>
      {summary && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
            <p className="text-sm text-gray-500">Users</p>
            <p className="text-2xl font-bold">{summary.users_total}</p>
          </div>
          <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
            <p className="text-sm text-gray-500">Approved</p>
            <p className="text-2xl font-bold">{summary.listings_approved}</p>
          </div>
          <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
            <p className="text-sm text-gray-500">Pending</p>
            <p className="text-2xl font-bold">{summary.listings_pending}</p>
          </div>
          <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
            <p className="text-sm text-gray-500">Revenue</p>
            <p className="text-2xl font-bold">${summary.revenue_completed_total.toFixed(2)}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-100 p-4 h-72">
        <h2 className="font-semibold mb-2">Listings by city</h2>
        <ResponsiveContainer width="100%" height="85%">
          <BarChart data={cityRows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="city" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#2D9CDB" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="p-4 border-b flex flex-wrap gap-3 items-center justify-between">
          <h2 className="font-semibold">Pending listings</h2>
          <input
            className="border rounded-lg px-3 py-2 text-sm"
            placeholder="Moderation note"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="p-3">Title</th>
                <th className="p-3">City</th>
                <th className="p-3">Rent</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {pending.map((row) => (
                <tr key={row.id} className="border-t">
                  <td className="p-3">{row.title}</td>
                  <td className="p-3">{row.city}</td>
                  <td className="p-3">PKR {row.rent_monthly.toLocaleString()}</td>
                  <td className="p-3 space-x-2">
                    <button
                      type="button"
                      className="px-3 py-1 rounded-lg bg-success text-white text-xs"
                      onClick={() => void moderate(row.id, "approved")}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className="px-3 py-1 rounded-lg bg-red-600 text-white text-xs"
                      onClick={() => void moderate(row.id, "rejected")}
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
