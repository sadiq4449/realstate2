import { Navbar } from "./Navbar";

/** App shell with sticky navbar and centered content column. */
export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-surface text-gray-900">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
