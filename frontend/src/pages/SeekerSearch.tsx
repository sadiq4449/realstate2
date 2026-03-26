import L from "leaflet";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap, useMapEvents } from "react-leaflet";
import { apiFetch } from "../api/client";
import { useAppDispatch, useAppSelector } from "../app/hooks";
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

function MapCenterReporter({ onCenter }: { onCenter: (lat: number, lng: number) => void }) {
  const map = useMapEvents({
    moveend() {
      const c = map.getCenter();
      onCenter(c.lat, c.lng);
    },
  });
  useEffect(() => {
    const c = map.getCenter();
    onCenter(c.lat, c.lng);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stable map instance
  }, [map]);
  return null;
}

/** Search filters + list/map toggle for seekers. */
export function SeekerSearch() {
  useFixLeafletIcons();
  const dispatch = useAppDispatch();
  const authUser = useAppSelector((s) => s.auth.user);
  const [city, setCity] = useState("Karachi");
  const [minBed, setMinBed] = useState<number | "">("");
  const [minBath, setMinBath] = useState<number | "">("");
  const [maxPrice, setMaxPrice] = useState<number | "">("");
  const [furnished, setFurnished] = useState<boolean | "">("");
  const [q, setQ] = useState("");
  const [radiusKm, setRadiusKm] = useState<number | "">("");
  const [mapCenter, setMapCenter] = useState({ lat: 24.86, lng: 67.01 });
  const reportMapCenter = useCallback((lat: number, lng: number) => {
    setMapCenter((prev) => (Math.abs(prev.lat - lat) < 1e-6 && Math.abs(prev.lng - lng) < 1e-6 ? prev : { lat, lng }));
  }, []);
  const [view, setView] = useState<"list" | "map">("list");
  const [items, setItems] = useState<Property[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [alertCity, setAlertCity] = useState("Karachi");
  const [alertMinPrice, setAlertMinPrice] = useState<number | "">("");
  const [alertMaxPrice, setAlertMaxPrice] = useState<number | "">("");
  const [alertMinBed, setAlertMinBed] = useState<number | "">("");
  const [alertMsg, setAlertMsg] = useState<string | null>(null);

  const params = useMemo(() => {
    const p = new URLSearchParams();
    if (city) p.set("city", city);
    if (minBed !== "") p.set("min_bedrooms", String(minBed));
    if (minBath !== "") p.set("min_bathrooms", String(minBath));
    if (maxPrice !== "") p.set("max_price", String(maxPrice));
    if (furnished !== "") p.set("furnished", String(furnished));
    if (q.trim()) p.set("q", q.trim());
    if (radiusKm !== "" && Number(radiusKm) > 0) {
      p.set("near_lat", String(mapCenter.lat));
      p.set("near_lng", String(mapCenter.lng));
      p.set("radius_m", String(Number(radiusKm) * 1000));
    }
    p.set("limit", "30");
    return p.toString();
  }, [city, minBed, minBath, maxPrice, furnished, q, radiusKm, mapCenter.lat, mapCenter.lng]);

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

  async function saveAlert(e: FormEvent) {
    e.preventDefault();
    setAlertMsg(null);
    if (authUser?.role !== "seeker") return;
    try {
      await apiFetch("/listing-alerts", {
        method: "POST",
        json: {
          city: alertCity,
          min_price: alertMinPrice === "" ? undefined : Number(alertMinPrice),
          max_price: alertMaxPrice === "" ? undefined : Number(alertMaxPrice),
          min_bedrooms: alertMinBed === "" ? undefined : Number(alertMinBed),
        },
      });
      setAlertMsg("Alert saved. We will notify you when matching listings go live.");
    } catch (ex) {
      setAlertMsg(ex instanceof Error ? ex.message : "Failed");
    }
  }

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
            <span className="text-gray-600">Min bathrooms</span>
            <input
              type="number"
              className="mt-1 w-full border rounded-lg px-2 py-2"
              value={minBath}
              onChange={(e) => setMinBath(e.target.value === "" ? "" : Number(e.target.value))}
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
          <label className="block text-sm">
            <span className="text-gray-600">Map radius (km)</span>
            <input
              type="number"
              className="mt-1 w-full border rounded-lg px-2 py-2"
              placeholder="Leave empty for city-wide"
              value={radiusKm}
              onChange={(e) => setRadiusKm(e.target.value === "" ? "" : Number(e.target.value))}
            />
            <span className="text-xs text-gray-500">Uses map center when you open the Map tab.</span>
          </label>
          <button
            type="button"
            onClick={() => void runSearch()}
            className="w-full py-2 rounded-lg bg-primary text-white font-medium hover:opacity-90"
          >
            {loading ? "Searching…" : "Apply"}
          </button>

          {authUser?.role === "seeker" && (
            <div className="border-t pt-4 space-y-2">
              <h3 className="text-sm font-semibold">New listing alerts</h3>
              <form className="space-y-2" onSubmit={saveAlert}>
                <input
                  className="w-full border rounded-lg px-2 py-2 text-sm"
                  value={alertCity}
                  onChange={(e) => setAlertCity(e.target.value)}
                  placeholder="City"
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    className="border rounded-lg px-2 py-1 text-xs"
                    placeholder="Min rent"
                    value={alertMinPrice === "" ? "" : alertMinPrice}
                    onChange={(e) => setAlertMinPrice(e.target.value === "" ? "" : Number(e.target.value))}
                  />
                  <input
                    type="number"
                    className="border rounded-lg px-2 py-1 text-xs"
                    placeholder="Max rent"
                    value={alertMaxPrice === "" ? "" : alertMaxPrice}
                    onChange={(e) => setAlertMaxPrice(e.target.value === "" ? "" : Number(e.target.value))}
                  />
                </div>
                <input
                  type="number"
                  className="w-full border rounded-lg px-2 py-1 text-xs"
                  placeholder="Min bedrooms (optional)"
                  value={alertMinBed === "" ? "" : alertMinBed}
                  onChange={(e) => setAlertMinBed(e.target.value === "" ? "" : Number(e.target.value))}
                />
                <button
                  type="submit"
                  className="w-full py-2 rounded-lg bg-gray-900 text-white text-xs font-medium"
                >
                  Save alert
                </button>
              </form>
              {alertMsg && <p className="text-xs text-gray-600">{alertMsg}</p>}
            </div>
          )}
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
                <MapCenterReporter onCenter={reportMapCenter} />
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
