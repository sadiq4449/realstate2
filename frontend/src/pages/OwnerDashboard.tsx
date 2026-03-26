import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAppDispatch } from "../app/hooks";
import { ListingCard } from "../components/ListingCard";
import { setMine, type Property } from "../slices/propertiesSlice";

type PerfRow = {
  property_id: string;
  title: string;
  status?: string;
  view_count: number;
  inquiries: number;
};

/** Owner listings + views / inquiries (Epic 2.4). */
export function OwnerDashboard() {
  const dispatch = useAppDispatch();
  const [items, setItems] = useState<Property[]>([]);
  const [perf, setPerf] = useState<PerfRow[]>([]);

  useEffect(() => {
    void (async () => {
      const data = (await apiFetch("/properties/mine")) as { items: Property[] };
      setItems(data.items);
      dispatch(setMine(data.items));
    })();
  }, [dispatch]);

  useEffect(() => {
    void (async () => {
      try {
        const s = (await apiFetch("/analytics/owner/summary")) as { listings: PerfRow[] };
        setPerf(s.listings);
      } catch {
        setPerf([]);
      }
    })();
  }, [items.length]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Owner dashboard</h1>
          <p className="text-gray-600 text-sm">Listings, views, and inquiries.</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/pricing"
            className="px-4 py-2 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 text-sm font-medium"
          >
            Subscription
          </Link>
          <Link
            to="/owner/new"
            className="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:opacity-90"
          >
            New listing
          </Link>
        </div>
      </div>

      {perf.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="p-4 border-b font-semibold">Performance</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="p-3">Listing</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Views</th>
                  <th className="p-3">Inquiries</th>
                </tr>
              </thead>
              <tbody>
                {perf.map((row) => (
                  <tr key={row.property_id} className="border-t">
                    <td className="p-3">{row.title}</td>
                    <td className="p-3 capitalize">{row.status}</td>
                    <td className="p-3">{row.view_count}</td>
                    <td className="p-3">{row.inquiries}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((p) => (
          <ListingCard key={p.id} p={p} />
        ))}
      </div>
      {items.length === 0 && (
        <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-200">
          <p className="text-gray-600 mb-4">No listings yet.</p>
          <Link to="/owner/new" className="text-primary font-semibold">
            Create your first listing
          </Link>
        </div>
      )}
    </div>
  );
}
