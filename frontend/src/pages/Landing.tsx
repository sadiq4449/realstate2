import { Link } from "react-router-dom";
import { ListingCard } from "../components/ListingCard";
import type { Property } from "../slices/propertiesSlice";

/** Marketing hero plus featured listings preview (static sample + optional API later). */
export function Landing({ featured }: { featured: Property[] }) {
  return (
    <div className="space-y-16">
      <section className="grid md:grid-cols-2 gap-10 items-center">
        <div className="space-y-6">
          <p className="text-primary font-semibold tracking-wide uppercase text-sm">RealStat</p>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
            Rent homes without friction
          </h1>
          <p className="text-lg text-gray-600">
            Owners list with subscriptions. Seekers search, map, and chat in real time. Admins keep
            quality high.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/search"
              className="inline-flex items-center justify-center px-6 py-3 rounded-xl bg-primary text-white font-semibold hover:opacity-90 active:scale-[0.99] transition"
            >
              Browse listings
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-gray-200 bg-white font-semibold hover:bg-gray-50"
            >
              List your property
            </Link>
          </div>
        </div>
        <div className="rounded-2xl overflow-hidden shadow-lg border border-gray-100 bg-white">
          <img
            src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200"
            alt="Modern home"
            className="w-full h-full object-cover aspect-[4/3]"
          />
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-6">
        {[
          { t: "Owners", d: "Listings, subscriptions, and lead inbox in one dashboard." },
          { t: "Seekers", d: "Filters, map view, and instant chat with verified owners." },
          { t: "Admins", d: "Moderation, analytics, and subscription pricing control." },
        ].map((x) => (
          <div key={x.t} className="p-6 rounded-xl bg-white border border-gray-100 shadow-sm">
            <h3 className="font-semibold text-lg mb-2">{x.t}</h3>
            <p className="text-gray-600 text-sm">{x.d}</p>
          </div>
        ))}
      </section>

      {featured.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Featured in Karachi</h2>
            <Link to="/search" className="text-primary font-medium hover:underline">
              View all
            </Link>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.map((p) => (
              <ListingCard key={p.id} p={p} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
