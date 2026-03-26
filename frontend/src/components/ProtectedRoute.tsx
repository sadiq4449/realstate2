import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAppSelector } from "../app/hooks";
import type { UserRole } from "../slices/authSlice";

/** Redirects unauthenticated users or wrong roles to login/home. */
export function ProtectedRoute({
  children,
  roles,
}: {
  children: ReactNode;
  roles?: UserRole[];
}) {
  const { user, bootstrapped } = useAppSelector((s) => s.auth);
  if (!bootstrapped) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center text-gray-500">
        Loading session…
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}
