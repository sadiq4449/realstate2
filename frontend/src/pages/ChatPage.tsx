import { FormEvent, useEffect, useRef, useState } from "react";
import { apiBase, apiFetch, getToken } from "../api/client";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { appendMessage, setActiveConversation, setMessages, type ChatMessage } from "../slices/chatSlice";

type Thread = {
  conversation_id: string;
  property_id: string;
  other_user_id: string;
  other_user_name: string;
  last_message: string;
  last_at: string;
};

function wsBaseUrl() {
  const env = import.meta.env.VITE_WS_URL;
  if (env) return env.replace(/\/$/, "");
  const { protocol, hostname } = window.location;
  const wsProto = protocol === "https:" ? "wss" : "ws";
  return `${wsProto}://${hostname}:8000`;
}

/** Inbox + thread view with WebSocket join for live updates. */
export function ChatPage() {
  const user = useAppSelector((s) => s.auth.user);
  const { activeConversationId, messages } = useAppSelector((s) => s.chat);
  const dispatch = useAppDispatch();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [body, setBody] = useState("");
  const [propertyId, setPropertyId] = useState("");
  const [recipientId, setRecipientId] = useState("");
  const [attachUrl, setAttachUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  async function onPickFile(f: File | null) {
    if (!f) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", f);
      const token = getToken();
      const res = await fetch(`${apiBase}/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: fd,
      });
      const data = (await res.json()) as { url?: string };
      if (!res.ok) throw new Error("Upload failed");
      if (data.url) setAttachUrl(data.url);
    } catch {
      setAttachUrl(null);
    } finally {
      setUploading(false);
    }
  }

  async function refreshThreads() {
    const rows = (await apiFetch("/messages/conversations")) as Thread[];
    setThreads(rows);
  }

  useEffect(() => {
    void refreshThreads();
  }, []);

  useEffect(() => {
    if (!activeConversationId) return;
    void (async () => {
      const rows = (await apiFetch(`/messages/${activeConversationId}`)) as ChatMessage[];
      dispatch(setMessages(rows));
    })();
  }, [activeConversationId, dispatch]);

  useEffect(() => {
    const token = getToken();
    if (!token || !user) return;
    const ws = new WebSocket(`${wsBaseUrl()}/ws/chat?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string) as { type: string; payload?: ChatMessage };
        if (data.type === "message" && data.payload) {
          dispatch(appendMessage(data.payload));
        }
      } catch {
        /* ignore */
      }
    };
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [user, dispatch]);

  useEffect(() => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN || !activeConversationId) return;
    ws.send(JSON.stringify({ action: "join", conversation_id: activeConversationId }));
  }, [activeConversationId]);

  async function startThread(e: FormEvent) {
    e.preventDefault();
    if (!propertyId || !recipientId || !body) return;
    await apiFetch("/messages", {
      method: "POST",
      json: { property_id: propertyId, recipient_id: recipientId, body, attachment_url: attachUrl || undefined },
    });
    setBody("");
    setAttachUrl(null);
    await refreshThreads();
  }

  async function sendReply(e: FormEvent) {
    e.preventDefault();
    if (!activeConversationId || !body.trim()) return;
    const t = threads.find((x) => x.conversation_id === activeConversationId);
    if (!t) return;
    await apiFetch("/messages", {
      method: "POST",
      json: {
        property_id: t.property_id,
        recipient_id: t.other_user_id,
        body,
        attachment_url: attachUrl || undefined,
      },
    });
    setBody("");
    setAttachUrl(null);
    await refreshThreads();
    const rows = (await apiFetch(`/messages/${activeConversationId}`)) as ChatMessage[];
    dispatch(setMessages(rows));
  }

  return (
    <div className="grid lg:grid-cols-[280px_1fr] gap-4 min-h-[520px]">
      <aside className="bg-white border border-gray-100 rounded-xl p-3 space-y-2">
        <h2 className="font-semibold px-2">Inbox</h2>
        <div className="space-y-1 max-h-[440px] overflow-y-auto">
          {threads.map((t) => (
            <button
              key={t.conversation_id}
              type="button"
              onClick={() => dispatch(setActiveConversation(t.conversation_id))}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
                activeConversationId === t.conversation_id ? "bg-primary/10 text-primary" : "hover:bg-gray-50"
              }`}
            >
              <div className="font-medium line-clamp-1">{t.other_user_name}</div>
              <div className="text-xs text-gray-500 line-clamp-2">{t.last_message}</div>
            </button>
          ))}
        </div>
        <form className="space-y-2 border-t pt-3 px-2" onSubmit={startThread}>
          <p className="text-xs text-gray-500">Start thread (ids)</p>
          <input
            className="w-full border rounded px-2 py-1 text-xs"
            placeholder="Property ID"
            value={propertyId}
            onChange={(e) => setPropertyId(e.target.value)}
          />
          <input
            className="w-full border rounded px-2 py-1 text-xs"
            placeholder="Recipient user ID"
            value={recipientId}
            onChange={(e) => setRecipientId(e.target.value)}
          />
          <input
            className="w-full border rounded px-2 py-1 text-xs"
            placeholder="Message"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
          <button type="submit" className="w-full py-1 rounded bg-gray-900 text-white text-xs">
            Send
          </button>
        </form>
      </aside>
      <section className="bg-white border border-gray-100 rounded-xl flex flex-col">
        <div className="border-b px-4 py-3 font-semibold">
          {activeConversationId ? "Conversation" : "Select a thread"}
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((m) => {
            const mine = m.sender_id === user?.id;
            return (
              <div key={m.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
                    mine ? "bg-primary text-white" : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p>{m.body}</p>
                  {m.attachment_url && (
                    <a
                      href={m.attachment_url}
                      className={`text-xs underline mt-1 block ${mine ? "text-white/90" : "text-primary"}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Attachment
                    </a>
                  )}
                  <p className={`text-[10px] mt-1 ${mine ? "text-white/80" : "text-gray-500"}`}>
                    {new Date(m.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
        {activeConversationId && (
          <form onSubmit={sendReply} className="border-t p-3 flex flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <label className="text-gray-600">
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => void onPickFile(e.target.files?.[0] ?? null)}
                />
                <span className="px-2 py-1 rounded border border-gray-200 cursor-pointer">
                  {uploading ? "Uploading…" : "Attach file"}
                </span>
              </label>
              {attachUrl && <span className="text-success">File ready</span>}
            </div>
            <div className="flex gap-2">
              <input
                className="flex-1 border rounded-lg px-3 py-2 text-sm"
                placeholder="Reply…"
                value={body}
                onChange={(e) => setBody(e.target.value)}
              />
              <button type="submit" className="px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium">
                Send
              </button>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}
