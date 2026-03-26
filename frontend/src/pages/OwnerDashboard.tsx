import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAppDispatch } from "../app/hooks";
import { ListingCard } from "../components/ListingCard";
import { setMine, type Property } from "../slices/propertiesSlice";

export function OwnerDashboard() {
  const dispatch = useAppDispatch();
  const [items, setItems] = useState<Property[]>([]);

  useEffect(() => {
    void (async () => {
      const data = (await apiFetch("/properties/mine")) as { items: Property[] };
      setItems(data.items);
      dispatch(setMine(data.items));
    })();
  }, [dispatch]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Owner dashboard</h1>
          <p className="text-gray-600 text-sm">Manage listings and subscription.</p>
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
