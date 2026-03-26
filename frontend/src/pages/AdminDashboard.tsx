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
import type { User } from "../slices/authSlice";

type Summary = {
  users_total: number;
  listings_pending: number;
  listings_approved: number;
  revenue_completed_total: number;
  complaints_open?: number;
};

type ChatRow = {
  id: string;
  body: string;
  sender_id: string;
  recipient_id: string;
  property_id: string;
  attachment_url?: string | null;
  created_at?: string;
};

/** Admin analytics, moderation, users, chat monitor (Epic 4.4, 6.x). */
export function AdminDashboard() {
  const [tab, setTab] = useState<"overview" | "users" | "chats">("overview");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [cityRows, setCityRows] = useState<{ city: string; count: number }[]>([]);
  const [pending, setPending] = useState<Property[]>([]);
  const [reason, setReason] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [chats, setChats] = useState<ChatRow[]>([]);

  async function refresh() {
    const s = (await apiFetch("/analytics/summary")) as Summary;
    const c = (await apiFetch("/analytics/listings-by-city")) as { city: string; count: number }[];
    const p = (await apiFetch("/admin/properties/pending")) as { items: Property[] };
    setSummary(s);
    setCityRows(c);
    setPending(p.items);
  }

  async function loadUsers() {
    const data = (await apiFetch("/users/admin/list?limit=100")) as { items: User[] };
    setUsers(data.items);
  }

  async function loadChats() {
    const rows = (await apiFetch("/admin/messages/recent?limit=80")) as ChatRow[];
    setChats(rows);
  }

  useEffect(() => {
    void refresh();
  }, []);

  useEffect(() => {
    if (tab === "users") void loadUsers();
    if (tab === "chats") void loadChats();
  }, [tab]);

  async function moderate(id: string, status: "approved" | "rejected") {
    await apiFetch(`/admin/properties/${id}/moderate`, {
      method: "POST",
      json: { status, reason: reason || undefined },
    });
    await refresh();
  }

  async function toggleUserActive(u: User, active: boolean) {
    await apiFetch(`/users/admin/${u.id}`, {
      method: "PATCH",
      json: { is_active: active },
    });
    await loadUsers();
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Admin</h1>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {(["overview", "users", "chats"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${
              tab === t ? "bg-primary text-white" : "bg-gray-100 text-gray-700"
            }`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <>
          {summary && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
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
              <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
                <p className="text-sm text-gray-500">Complaints (open)</p>
                <p className="text-2xl font-bold">{summary.complaints_open ?? 0}</p>
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
        </>
      )}

      {tab === "users" && (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="p-4 border-b font-semibold">Manage users</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="p-3">Name</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Role</th>
                  <th className="p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-t">
                    <td className="p-3">{u.full_name}</td>
                    <td className="p-3">{u.email}</td>
                    <td className="p-3 capitalize">{u.role}</td>
                    <td className="p-3">
                      <button
                        type="button"
                        className="text-xs text-primary font-medium mr-2"
                        onClick={() => void toggleUserActive(u, true)}
                      >
                        Activate
                      </button>
                      <button
                        type="button"
                        className="text-xs text-red-600 font-medium"
                        onClick={() => void toggleUserActive(u, false)}
                      >
                        Block
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "chats" && (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="p-4 border-b font-semibold">Recent messages (monitoring)</div>
          <div className="max-h-[520px] overflow-y-auto divide-y text-sm">
            {chats.map((m) => (
              <div key={m.id} className="p-3 space-y-1">
                <p className="text-gray-800">{m.body}</p>
                <p className="text-xs text-gray-500">
                  Property {m.property_id} · {m.created_at && new Date(m.created_at).toLocaleString()}
                  {m.attachment_url && (
                    <a href={m.attachment_url} className="ml-2 text-primary" target="_blank" rel="noreferrer">
                      Attachment
                    </a>
                  )}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
