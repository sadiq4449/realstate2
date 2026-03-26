import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch, setToken } from "../api/client";
import { useAppDispatch } from "../app/hooks";
import { setUser, type User, type UserRole } from "../slices/authSlice";

/** Registration with role selection for owner vs seeker. */
export function Register() {
  const nav = useNavigate();
  const dispatch = useAppDispatch();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<UserRole>("seeker");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        json: { email, password, full_name: fullName, role },
      });
      const data = (await apiFetch("/auth/login", {
        method: "POST",
        json: { email, password },
      })) as { access_token: string };
      setToken(data.access_token);
      const me = (await apiFetch("/users/me")) as User;
      dispatch(setUser(me));
      nav("/search");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Register failed");
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
      <h1 className="text-2xl font-bold mb-6">Create account</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <div>
          <label className="block text-sm font-medium mb-1">Full name</label>
          <input
            className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary outline-none"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
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
          <label className="block text-sm font-medium mb-1">Password (min 8)</label>
          <input
            className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            minLength={8}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">I am a</label>
          <select
            className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary outline-none"
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
          >
            <option value="seeker">Rent seeker</option>
            <option value="owner">Property owner</option>
          </select>
        </div>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-primary text-white font-semibold hover:opacity-90"
        >
          Create account
        </button>
      </form>
      <p className="text-sm text-gray-600 mt-4">
        Already have an account?{" "}
        <Link to="/login" className="text-primary font-medium">
          Login
        </Link>
      </p>
    </div>
  );
}
