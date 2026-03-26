import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch, setToken } from "../api/client";
import { useAppDispatch } from "../app/hooks";
import { setUser, type User } from "../slices/authSlice";

/** Email/password login; stores JWT and loads `/users/me`. */
export function Login() {
  const nav = useNavigate();
  const dispatch = useAppDispatch();
  const [email, setEmail] = useState("seeker@demo.com");
  const [password, setPassword] = useState("password123");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const data = (await apiFetch("/auth/login", {
        method: "POST",
        json: { email, password },
      })) as { access_token: string };
      setToken(data.access_token);
      const me = (await apiFetch("/users/me")) as User;
      dispatch(setUser(me));
      nav(me.role === "admin" ? "/admin" : me.role === "owner" ? "/owner" : "/search");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Login failed");
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
      <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
      <p className="text-gray-600 text-sm mb-6">
        Demo seeker: seeker@demo.com (after seed).
      </p>
      <form className="space-y-4" onSubmit={onSubmit}>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
        </div>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-primary text-white font-semibold hover:opacity-90"
        >
          Sign in
        </button>
      </form>
      <p className="text-sm text-gray-600 mt-4">
        No account?{" "}
        <Link to="/register" className="text-primary font-medium">
          Register
        </Link>
      </p>
    </div>
  );
}
