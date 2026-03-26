import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { setUser, type User } from "../slices/authSlice";

/** Update profile (Epic 1.4). */
export function ProfilePage() {
  const user = useAppSelector((s) => s.auth.user);
  const dispatch = useAppDispatch();
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
      setPhone(user.phone ?? "");
    }
  }, [user]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setMsg(null);
    try {
      const updated = (await apiFetch("/users/me", {
        method: "PATCH",
        json: { full_name: fullName, phone: phone || null },
      })) as User;
      dispatch(setUser(updated));
      setMsg("Profile saved.");
    } catch (ex) {
      setMsg(ex instanceof Error ? ex.message : "Failed");
    }
  }

  if (!user) {
    return <p className="text-gray-600">Login to manage your profile.</p>;
  }

  return (
    <div className="max-w-lg mx-auto bg-white rounded-2xl border border-gray-100 shadow-sm p-8 space-y-4">
      <h1 className="text-2xl font-bold">Profile</h1>
      <p className="text-sm text-gray-500">
        {user.email} · {user.role}
      </p>
      <form className="space-y-4" onSubmit={onSubmit}>
        <div>
          <label className="block text-sm font-medium mb-1">Full name</label>
          <input
            className="w-full border rounded-lg px-3 py-2"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Phone</label>
          <input
            className="w-full border rounded-lg px-3 py-2"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+92-300-0000000"
          />
        </div>
        {msg && <p className="text-sm text-primary">{msg}</p>}
        <button type="submit" className="w-full py-3 rounded-xl bg-primary text-white font-semibold">
          Save changes
        </button>
      </form>
    </div>
  );
}
