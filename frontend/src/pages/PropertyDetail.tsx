import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAppSelector } from "../app/hooks";
import { ImageSlider } from "../components/ImageSlider";
import type { Property } from "../slices/propertiesSlice";

/** Listing detail with contact CTA for seekers. */
export function PropertyDetail() {
  const { id } = useParams();
  const user = useAppSelector((s) => s.auth.user);
  const [p, setP] = useState<Property | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [sent, setSent] = useState(false);

  useEffect(() => {
    if (!id) return;
    void (async () => {
      try {
        const data = (await apiFetch(`/properties/${id}`)) as Property;
        setP(data);
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Failed to load");
      }
    })();
  }, [id]);

  async function sendMessage(e: FormEvent) {
    e.preventDefault();
    if (!p || !user || user.role !== "seeker") return;
    if (!p.owner_id) return;
    await apiFetch("/messages", {
      method: "POST",
      json: { property_id: p.id, recipient_id: p.owner_id, body: msg },
    });
    setSent(true);
    setMsg("");
  }

  if (err) return <p className="text-red-600">{err}</p>;
  if (!p) return <p className="text-gray-500">Loading…</p>;

  return (
    <div className="grid lg:grid-cols-2 gap-8">
      <div>
        <ImageSlider images={p.images} alt={p.title} />
      </div>
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">{p.title}</h1>
        <p className="text-primary text-2xl font-semibold">PKR {p.rent_monthly.toLocaleString()} / mo</p>
        <p className="text-gray-600">{p.city}</p>
        <p className="text-gray-700 whitespace-pre-wrap">{p.description}</p>
        <div className="flex flex-wrap gap-2 text-sm">
          {p.amenities.map((a) => (
            <span key={a} className="px-2 py-1 rounded-full bg-gray-100">
              {a}
            </span>
          ))}
        </div>

        {user?.role === "seeker" && (
          <form onSubmit={sendMessage} className="space-y-3 border-t pt-4">
            <h3 className="font-semibold">Message owner</h3>
            <textarea
              className="w-full border rounded-lg p-3 min-h-[100px]"
              value={msg}
              onChange={(e) => setMsg(e.target.value)}
              placeholder="Ask about availability, deposit, etc."
              required
            />
            <button type="submit" className="px-4 py-2 rounded-lg bg-primary text-white font-medium">
              Send via platform
            </button>
            {sent && <p className="text-success text-sm">Sent. Check Chat for replies.</p>}
          </form>
        )}

        {!user && (
          <p className="text-sm text-gray-600">
            <Link to="/login" className="text-primary font-medium">
              Login as seeker
            </Link>{" "}
            to contact the owner.
          </p>
        )}
        <p className="text-xs text-gray-400">Owner ID: {ownerId}</p>
      </div>
    </div>
  );
}
