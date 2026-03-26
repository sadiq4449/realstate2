import L from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { apiFetch } from "../api/client";
import { useAppDispatch } from "../app/hooks";
import { ListingCard } from "../components/ListingCard";
import { setSearch, type Property } from "../slices/propertiesSlice";
import "leaflet/dist/leaflet.css";

/** Fix default marker assets in Vite bundle. */
function useFixLeafletIcons() {
  useEffect(() => {
    delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    });
  }, []);
}

function MapBounds({ items }: { items: Property[] }) {
  const map = useMap();
  useEffect(() => {
    const pts = items
      .map((p) => p.location?.coordinates)
      .filter(Boolean) as number[][];
    if (!pts.length) return;
    const b = L.latLngBounds(pts.map(([lng, lat]) => [lat, lng]));
    map.fitBounds(b.pad(0.2));
  }, [items, map]);
  return null;
}

/** Search filters + list/map toggle for seekers. */
export function SeekerSearch() {
  useFixLeafletIcons();
  const dispatch = useAppDispatch();
  const [city, setCity] = useState("Karachi");
  const [minBed, setMinBed] = useState<number | "">("");
  const [maxPrice, setMaxPrice] = useState<number | "">("");
  const [furnished, setFurnished] = useState<boolean | "">("");
  const [q, setQ] = useState("");
  const [view, setView] = useState<"list" | "map">("list");
  const [items, setItems] = useState<Property[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const params = useMemo(() => {
    const p = new URLSearchParams();
    if (city) p.set("city", city);
    if (minBed !== "") p.set("min_bedrooms", String(minBed));
    if (maxPrice !== "") p.set("max_price", String(maxPrice));
    if (furnished !== "") p.set("furnished", String(furnished));
    if (q.trim()) p.set("q", q.trim());
    p.set("limit", "30");
    return p.toString();
  }, [city, minBed, maxPrice, furnished, q]);

  async function runSearch() {
    setLoading(true);
    try {
      const data = (await apiFetch(`/search/properties?${params}`)) as {
        items: Property[];
        total: number;
      };
      setItems(data.items);
      setTotal(data.total);
      dispatch(setSearch({ items: data.items, total: data.total }));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <aside className="lg:w-72 shrink-0 space-y-4 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="font-semibold">Filters</h2>
          <label className="block text-sm">
            <span className="text-gray-600">Keyword</span>
            <input
              className="mt-1 w-full border rounded-lg px-2 py-2"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Sea view, DHA…"
            />
          </label>
          <label className="block text-sm">
            <span className="text-gray-600">City</span>
            <input
              className="mt-1 w-full border rounded-lg px-2 py-2"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            <span className="text-gray-600">Min bedrooms</span>
            <input
              type="number"
              className="mt-1 w-full border rounded-lg px-2 py-2"
              value={minBed}
              onChange={(e) => setMinBed(e.target.value === "" ? "" : Number(e.target.value))}
            />
          </label>
          <label className="block text-sm">
            <span className="text-gray-600">Max price (PKR)</span>
            <input
              type="number"
              className="mt-1 w-full border rounded-lg px-2 py-2"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value === "" ? "" : Number(e.target.value))}
            />
          </label>
          <label className="block text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={furnished === true}
              onChange={(e) => setFurnished(e.target.checked ? true : "")}
            />
            Furnished only
          </label>
          <button
            type="button"
            onClick={() => void runSearch()}
            className="w-full py-2 rounded-lg bg-primary text-white font-medium hover:opacity-90"
          >
            {loading ? "Searching…" : "Apply"}
          </button>
        </aside>

        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-gray-600 text-sm">
              {total} listings found — toggle map for geo context.
            </p>
            <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
              <button
                type="button"
                className={`px-3 py-1 rounded-md text-sm ${view === "list" ? "bg-primary text-white" : ""}`}
                onClick={() => setView("list")}
              >
                List
              </button>
              <button
                type="button"
                className={`px-3 py-1 rounded-md text-sm ${view === "map" ? "bg-primary text-white" : ""}`}
                onClick={() => setView("map")}
              >
                Map
              </button>
            </div>
          </div>

          {view === "list" ? (
            <div className="grid sm:grid-cols-2 gap-6">
              {items.map((p) => (
                <ListingCard key={p.id} p={p} />
              ))}
            </div>
          ) : (
            <div className="h-[480px] rounded-xl overflow-hidden border border-gray-200 shadow-sm">
              <MapContainer center={[24.86, 67.01]} zoom={11} className="h-full w-full">
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <MapBounds items={items} />
                {items.map((p) => {
                  const c = p.location?.coordinates;
                  if (!c) return null;
                  const [lng, lat] = c;
                  return (
                    <Marker key={p.id} position={[lat, lng]}>
                      <Popup>
                        <div className="text-sm font-semibold">{p.title}</div>
                        <div>PKR {p.rent_monthly.toLocaleString()}</div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MapContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
