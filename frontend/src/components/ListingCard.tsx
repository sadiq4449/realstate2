import { Link } from "react-router-dom";
import type { Property } from "../slices/propertiesSlice";
import { ImageSlider } from "./ImageSlider";

/** Card used on landing, search, and dashboards with price pill and meta chips. */
export function ListingCard({ p }: { p: Property }) {
  return (
    <Link
      to={`/property/${p.id}`}
      className="block bg-white rounded-xl shadow-sm hover:shadow-md transition border border-gray-100 overflow-hidden focus:outline-none focus:ring-2 focus:ring-primary"
    >
      <div className="relative">
        <ImageSlider images={p.images} alt={p.title} />
        <span className="absolute top-3 right-3 bg-primary text-white text-sm font-semibold px-3 py-1 rounded-full">
          PKR {p.rent_monthly.toLocaleString()}
        </span>
      </div>
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-lg text-gray-900 line-clamp-1">{p.title}</h3>
        <p className="text-sm text-gray-500">{p.city}</p>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 rounded-full bg-gray-100">{p.bedrooms} bd</span>
          <span className="px-2 py-1 rounded-full bg-gray-100">{p.bathrooms} ba</span>
          {p.furnished && (
            <span className="px-2 py-1 rounded-full bg-success/10 text-success">Furnished</span>
          )}
        </div>
      </div>
    </Link>
  );
}
