import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { ListingCard } from "../components/ListingCard";
import type { Property } from "../slices/propertiesSlice";

/** Saved listings (Epic 3.3). */
export function FavoritesPage() {
  const [items, setItems] = useState<Property[]>([]);

  useEffect(() => {
    void (async () => {
      try {
        const data = (await apiFetch("/favorites")) as { items: Property[] };
        setItems(data.items);
      } catch {
        setItems([]);
      }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Saved listings</h1>
      <div className="grid sm:grid-cols-2 gap-6">
        {items.map((p) => (
          <ListingCard key={p.id} p={p} />
        ))}
      </div>
      {items.length === 0 && <p className="text-gray-600">No favorites yet. Save from a listing page.</p>}
    </div>
  );
}
