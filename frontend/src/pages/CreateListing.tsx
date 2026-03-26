import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";

export function CreateListing() {
  const nav = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [city, setCity] = useState("Karachi");
  const [address, setAddress] = useState("");
  const [rent, setRent] = useState(150000);
  const [bedrooms, setBedrooms] = useState(2);
  const [bathrooms, setBathrooms] = useState(2);
  const [furnished, setFurnished] = useState(false);
  const [amenities, setAmenities] = useState("parking,ac");
  const [lat, setLat] = useState(24.86);
  const [lng, setLng] = useState(67.01);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const list = amenities.split(",").map((s) => s.trim()).filter(Boolean);
      await apiFetch("/properties", {
        method: "POST",
        json: {
          title,
          description,
          city,
          address,
          rent_monthly: rent,
          bedrooms,
          bathrooms,
          furnished,
          amenities: list,
          images: [],
          latitude: lat,
          longitude: lng,
        },
      });
      nav("/owner");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Failed");
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
      <h1 className="text-2xl font-bold mb-6">New listing</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <input
          className="w-full border rounded-lg px-3 py-2"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <textarea
          className="w-full border rounded-lg px-3 py-2 min-h-[120px]"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <div className="grid sm:grid-cols-2 gap-3">
          <input className="border rounded-lg px-3 py-2" value={city} onChange={(e) => setCity(e.target.value)} />
          <input
            className="border rounded-lg px-3 py-2"
            placeholder="Address"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            required
          />
        </div>
        <div className="grid sm:grid-cols-3 gap-3">
          <input type="number" className="border rounded-lg px-3 py-2" value={rent} onChange={(e) => setRent(Number(e.target.value))} />
          <input type="number" className="border rounded-lg px-3 py-2" value={bedrooms} onChange={(e) => setBedrooms(Number(e.target.value))} />
          <input type="number" className="border rounded-lg px-3 py-2" value={bathrooms} onChange={(e) => setBathrooms(Number(e.target.value))} />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={furnished} onChange={(e) => setFurnished(e.target.checked)} />
          Furnished
        </label>
        <input className="w-full border rounded-lg px-3 py-2" value={amenities} onChange={(e) => setAmenities(e.target.value)} />
        <div className="grid sm:grid-cols-2 gap-3">
          <input type="number" step="any" className="border rounded-lg px-3 py-2" value={lat} onChange={(e) => setLat(Number(e.target.value))} />
          <input type="number" step="any" className="border rounded-lg px-3 py-2" value={lng} onChange={(e) => setLng(Number(e.target.value))} />
        </div>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button type="submit" className="w-full py-3 rounded-xl bg-primary text-white font-semibold">
          Submit for approval
        </button>
      </form>
    </div>
  );
}
