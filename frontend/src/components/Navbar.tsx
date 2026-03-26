import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { apiFetch, setToken } from "../api/client";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { logout } from "../slices/authSlice";

const linkCls = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-lg text-sm font-medium transition ${
    isActive ? "bg-primary/10 text-primary" : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
  }`;

/** Top navigation with role-aware links and auth actions. */
export function Navbar() {
  const user = useAppSelector((s) => s.auth.user);
  const dispatch = useAppDispatch();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!user) {
      setUnread(0);
      return;
    }
    void (async () => {
      try {
        const r = (await apiFetch("/notifications/unread-count")) as { count: number };
        setUnread(r.count);
      } catch {
        setUnread(0);
      }
    })();
  }, [user]);

  return (
    <header className="border-b border-gray-200 bg-white/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        <Link to="/" className="font-bold text-primary text-lg">
          RealStat
        </Link>
        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/search" className={linkCls}>
            Search
          </NavLink>
          {user?.role === "owner" && (
            <NavLink to="/owner" className={linkCls}>
              Owner
            </NavLink>
          )}
          {user?.role === "admin" && (
            <NavLink to="/admin" className={linkCls}>
              Admin
            </NavLink>
          )}
          <NavLink to="/pricing" className={linkCls}>
            Pricing
          </NavLink>
          {user && (
            <NavLink to="/chat" className={linkCls}>
              Chat
            </NavLink>
          )}
          {user && (
            <NavLink to="/notifications" className={linkCls}>
              Alerts{unread > 0 ? ` (${unread})` : ""}
            </NavLink>
          )}
          {user?.role === "seeker" && (
            <NavLink to="/favorites" className={linkCls}>
              Saved
            </NavLink>
          )}
          {user && (
            <NavLink to="/profile" className={linkCls}>
              Profile
            </NavLink>
          )}
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="text-sm text-gray-600 hidden sm:inline">{user.full_name}</span>
              <button
                type="button"
                className="text-sm px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50"
                onClick={() => {
                  setToken(null);
                  dispatch(logout());
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="text-sm px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
