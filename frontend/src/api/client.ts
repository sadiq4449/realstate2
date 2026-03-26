/**
 * Thin fetch wrapper with JWT header injection.
 *
 * In Vite dev we default to same-origin `/api/v1` so requests go through the dev-server
 * proxy (see vite.config.ts). That avoids "Failed to fetch" from:
 * - backend only listening on 127.0.0.1 while the page uses localhost (or the reverse)
 * - CORS / mixed host issues between localhost and 127.0.0.1
 *
 * Set `VITE_USE_API_PROXY=0` and `VITE_API_URL=http://127.0.0.1:8000/api/v1` to call the API directly.
 */

const envUrl = import.meta.env.VITE_API_URL?.trim().replace(/\/$/, "") ?? "";
const useDevProxy =
  import.meta.env.DEV && import.meta.env.VITE_USE_API_PROXY !== "0";

const API_BASE = useDevProxy
  ? "/api/v1"
  : envUrl.length > 0
    ? envUrl
    : "/api/v1";

export function getToken(): string | null {
  return localStorage.getItem("rs_token");
}

export function setToken(t: string | null) {
  if (t) localStorage.setItem("rs_token", t);
  else localStorage.removeItem("rs_token");
}

type Opt = RequestInit & { json?: unknown };

/** Performs authenticated JSON request; throws on non-OK with detail message. */
export async function apiFetch(path: string, opts: Opt = {}) {
  const headers: Record<string, string> = {
    ...(opts.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  let body = opts.body;
  if (opts.json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.json);
  }
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers, body });
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    let msg = res.statusText;
    if (typeof data === "object" && data && "detail" in data) {
      const d = (data as { detail: unknown }).detail;
      msg = Array.isArray(d) ? JSON.stringify(d) : String(d);
    }
    throw new Error(msg);
  }
  return data;
}

/** Download binary/text with auth (e.g. invoice). */
export async function apiDownload(path: string): Promise<Blob> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.blob();
}

export const apiBase = API_BASE;
