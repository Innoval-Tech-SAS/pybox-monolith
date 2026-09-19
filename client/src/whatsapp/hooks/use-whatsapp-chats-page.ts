import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToast } from "@/context/toast-context";
import { playMessageSound } from "../../chat/utils/chat-sound";
import type {
  WhatsAppChat,
  WhatsAppChatsPage,
  WhatsAppMessage,
  WsWhatsAppEvent,
} from "../types/whatsapp-chat-types";
import { useWhatsAppWebSocket } from "./use-whatsapp-websocket";

interface ThreadState {
  chatId: string;
  messages: WhatsAppMessage[];
  loading: boolean;
}

// Ventana de servicio al cliente de Meta: solo se puede enviar texto libre dentro de
// las 24h posteriores al último mensaje ENTRANTE del deudor — el backend también lo
// valida (fuente de verdad), esto es solo para deshabilitar el input proactivamente.
const CUSTOMER_SERVICE_WINDOW_MS = 24 * 60 * 60 * 1000;
const RECHECK_INTERVAL_MS = 60 * 1000;

/**
 * `chatId` y `organizationId` salen de los search params (?chat=&org=), que son la
 * fuente de verdad del hilo abierto: la lista mezcla varias organizaciones, así que
 * cada operación sobre un hilo necesita la organización a la que pertenece.
 */
export const useWhatsAppChatsPage = (chatId: string, organizationId: string) => {
  const { error: toastError } = useToast();
  const [chats, setChats] = useState<WhatsAppChat[]>([]);
  const [chatsLoading, setChatsLoading] = useState(true);
  const [selected, setSelected] = useState<ThreadState | null>(null);
  const [sending, setSending] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const loadedRef = useRef(false);

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), RECHECK_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  const handleWsEvent = useCallback((event: WsWhatsAppEvent) => {
    if (event.event === "new_message") {
      const msg = event.data;
      playMessageSound();
      setSelected((prev) =>
        prev?.chatId === msg.chatId && !prev.messages.some((m) => m.id === msg.id)
          ? { ...prev, messages: [...prev.messages, msg] }
          : prev,
      );
      setChats((prev) => {
        const exists = prev.some((c) => c.id === msg.chatId);
        if (!exists) return prev;
        const updated = prev.map((c) =>
          c.id === msg.chatId ? { ...c, lastMessageAt: msg.sentAt } : c,
        );
        return [...updated].sort((a, b) => (b.lastMessageAt ?? "").localeCompare(a.lastMessageAt ?? ""));
      });
    }
  }, []);

  const { request } = useWhatsAppWebSocket(handleWsEvent);

  // Sin organizationId el backend devuelve los hilos de todas las organizaciones
  // donde el usuario tenga el permiso, ya ordenados por último mensaje.
  const loadChats = useCallback(async () => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    setChatsLoading(true);
    try {
      const page = await request<WhatsAppChatsPage>("list_chats", { page: 1, pageSize: 50 });
      setChats(page.items ?? []);
    } catch {
      loadedRef.current = false;
    } finally {
      setChatsLoading(false);
    }
  }, [request]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  useEffect(() => {
    if (!chatId || !organizationId) {
      setSelected(null);
      return;
    }
    let cancelled = false;
    setSelected({ chatId, messages: [], loading: true });
    request<WhatsAppMessage[]>("list_messages", { organizationId, chatId })
      .then((messages) => {
        if (!cancelled) setSelected({ chatId, messages: messages ?? [], loading: false });
      })
      .catch(() => {
        if (!cancelled) {
          setSelected((prev) => (prev && prev.chatId === chatId ? { ...prev, loading: false } : prev));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [request, chatId, organizationId]);

  const sendMessage = useCallback(
    async (body: string): Promise<boolean> => {
      if (!selected) return false;
      setSending(true);
      try {
        const msg = await request<WhatsAppMessage>("send_message", {
          organizationId,
          chatId: selected.chatId,
          body,
        });
        setSelected((prev) =>
          prev && prev.chatId === msg.chatId && !prev.messages.some((m) => m.id === msg.id)
            ? { ...prev, messages: [...prev.messages, msg] }
            : prev,
        );
        setChats((prev) =>
          prev.map((c) => (c.id === msg.chatId ? { ...c, lastMessageAt: msg.sentAt } : c)),
        );
        return true;
      } catch (err) {
        toastError("No se pudo enviar el mensaje", err instanceof Error ? err.message : undefined);
        return false;
      } finally {
        setSending(false);
      }
    },
    [request, selected, organizationId, toastError],
  );

  const withinServiceWindow = useMemo(() => {
    if (!selected) return false;
    const lastInbound = [...selected.messages].reverse().find((m) => m.direction === "ENTRANTE");
    if (!lastInbound) return false;
    return now - new Date(lastInbound.sentAt).getTime() <= CUSTOMER_SERVICE_WINDOW_MS;
  }, [selected, now]);

  return { chats, chatsLoading, selected, sending, withinServiceWindow, sendMessage };
};
