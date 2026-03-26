import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";

type Row = {
  id: string;
  title: string;
  body: string;
  read: boolean;
  created_at?: string;
  data?: { property_id?: string };
};

/** In-app notification center (Epic 9.2). */
export function NotificationsPage() {
  const [rows, setRows] = useState<Row[]>([]);

  async function load() {
    const list = (await apiFetch("/notifications")) as Row[];
    setRows(
      list.map((r) => ({
        id: r.id,
        title: r.title,
        body: r.body,
        read: r.read,
        created_at: r.created_at,
        data: r.data,
      }))
    );
  }

  useEffect(() => {
    void load().catch(() => setRows([]));
  }, []);

  async function markRead(id: string) {
    await apiFetch(`/notifications/${id}/read`, { method: "POST" });
    await load();
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Notifications</h1>
      <ul className="space-y-2">
        {rows.map((n) => (
          <li
            key={n.id}
            className={`p-4 rounded-xl border ${n.read ? "bg-white border-gray-100" : "bg-primary/5 border-primary/20"}`}
          >
            <div className="font-semibold">{n.title}</div>
            <p className="text-sm text-gray-700 mt-1">{n.body}</p>
            <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
              {n.created_at && <span>{new Date(n.created_at).toLocaleString()}</span>}
              {n.data?.property_id && (
                <Link to={`/property/${n.data.property_id}`} className="text-primary font-medium">
                  View listing
                </Link>
              )}
              {!n.read && (
                <button type="button" className="text-primary font-medium" onClick={() => void markRead(n.id)}>
                  Mark read
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
      {rows.length === 0 && <p className="text-gray-600">No notifications yet.</p>}
    </div>
  );
}
