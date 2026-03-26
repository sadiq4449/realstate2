import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { apiFetch, getToken } from "./api/client";
import { useAppDispatch } from "./app/hooks";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminDashboard } from "./pages/AdminDashboard";
import { ChatPage } from "./pages/ChatPage";
import { CreateListing } from "./pages/CreateListing";
import { FavoritesPage } from "./pages/FavoritesPage";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { NotificationsPage } from "./pages/NotificationsPage";
import { OwnerDashboard } from "./pages/OwnerDashboard";
import { ProfilePage } from "./pages/ProfilePage";
import { PropertyDetail } from "./pages/PropertyDetail";
import { Register } from "./pages/Register";
import { SeekerSearch } from "./pages/SeekerSearch";
import { SubscriptionPage } from "./pages/SubscriptionPage";
import { setUser, type User } from "./slices/authSlice";
import type { Property } from "./slices/propertiesSlice";

/** Root routes and session bootstrap from stored JWT. */
export default function App() {
  const dispatch = useAppDispatch();
  const [featured, setFeatured] = useState<Property[]>([]);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      dispatch(setUser(null));
      return;
    }
    void (async () => {
      try {
        const me = (await apiFetch("/users/me")) as User;
        dispatch(setUser(me));
      } catch {
        dispatch(setUser(null));
      }
    })();
  }, [dispatch]);

  useEffect(() => {
    void (async () => {
      try {
        const data = (await apiFetch("/search/properties?limit=6")) as { items: Property[] };
        setFeatured(data.items);
      } catch {
        setFeatured([]);
      }
    })();
  }, []);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Landing featured={featured} />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/search" element={<SeekerSearch />} />
        <Route path="/property/:id" element={<PropertyDetail />} />
        <Route path="/pricing" element={<SubscriptionPage />} />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/favorites"
          element={
            <ProtectedRoute roles={["seeker"]}>
              <FavoritesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/owner"
          element={
            <ProtectedRoute roles={["owner"]}>
              <OwnerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/owner/new"
          element={
            <ProtectedRoute roles={["owner"]}>
              <CreateListing />
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
