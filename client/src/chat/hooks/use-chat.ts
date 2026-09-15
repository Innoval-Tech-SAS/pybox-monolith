import { useCallback, useRef, useState } from "react";
import { useApiClient } from "../../hooks/use-api-client";
import { useToast } from "@/context/toast-context";
import { playMessageSound } from "../utils/chat-sound";
import type {
  ChatAvailableUser,
  ChatMessage,
  ChatSummary,
  ChatWindow,
  MessagesPage,
  WsChatEvent,
} from "../../types/chat/chat-types";
import { useChatWebSocket } from "./use-chat-websocket";

const MAX_EXPANDED = 3;

export const useChat = () => {
  const { apiClient } = useApiClient();
  const { error: toastError } = useToast();
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [windows, setWindows] = useState<ChatWindow[]>([]);
  const [availableUsers, setAvailableUsers] = useState<ChatAvailableUser[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const loadedChats = useRef(false);

  const loadAvailableUsers = useCallback(async () => {
    try {
      const data = await apiClient("/users/available-for-chat");
      setAvailableUsers(data ?? []);
    } catch {
      // silent
    }
  }, [apiClient]);

  const handleWsEvent = useCallback(
    (event: WsChatEvent) => {
      if (event.event === "message") {
        const msg = event.data;
        playMessageSound();
        const win = windows.find((w) => w.chatId === msg.chatId);
        const winExpanded = win?.status === "expanded";
        const chatExists = chats.some((c) => c.id === msg.chatId);

        if (win) {
          setWindows((prev) =>
            prev.map((w) =>
              w.chatId === msg.chatId && !w.messages.some((m) => m.id === msg.id)
                ? { ...w, messages: [...w.messages, msg] }
                : w,
            ),
          );
        } else {
          const newWindow: ChatWindow = {
            chatId: msg.chatId,
            title: msg.senderName,
            peerAvatar: msg.senderAvatar,
            status: "minimized",
            messages: [msg],
            loading: true,
            nextCursor: null,
          };
          setWindows((prev) => [...prev, newWindow].slice(-MAX_EXPANDED));
          request<MessagesPage>("list_messages", { chatId: msg.chatId, limit: 50 })
            .then((page) => {
              setWindows((prev) =>
                prev.map((w) =>
                  w.chatId === msg.chatId
                    ? { ...w, messages: page.items ?? [], nextCursor: page.nextCursor, loading: false }
                    : w,
                ),
              );
            })
            .catch(() => {
              setWindows((prev) =>
                prev.map((w) => (w.chatId === msg.chatId ? { ...w, loading: false } : w)),
              );
            });
        }

        setChats((prev) => {
          if (chatExists) {
            return prev.map((c) =>
              c.id === msg.chatId
                ? {
                    ...c,
                    lastMessage: msg.body,
                    lastMessageAt: msg.createdAt,
                    unreadCount: winExpanded ? c.unreadCount : c.unreadCount + 1,
                  }
                : c,
            );
          }
          const newChat: ChatSummary = {
            id: msg.chatId,
            type: 0,
            title: msg.senderName,
            peerId: msg.senderId,
            peerAvatar: msg.senderAvatar,
            lastMessage: msg.body,
            lastMessageAt: msg.createdAt,
            unreadCount: 1,
          };
          return [newChat, ...prev];
        });

        if (winExpanded) {
          send("read", { chatId: msg.chatId, messageIds: [msg.id] });
        }
      } else if (event.event === "read") {
        const { chatId, messageIds } = event.data;
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === chatId
              ? {
                  ...w,
                  messages: w.messages.map((m) =>
                    messageIds.includes(m.id) ? { ...m, status: "read" as const } : m,
                  ),
                }
              : w,
          ),
        );
      }
    },
    [windows, chats],
  );

  const { send, request } = useChatWebSocket(handleWsEvent);

  const loadChats = useCallback(async () => {
    if (loadedChats.current) return;
    loadedChats.current = true;
    try {
      const data = await request<ChatSummary[]>("list_chats", {});
      setChats(data ?? []);
    } catch {
      // Sin el reset, un fallo dejaría el ref marcado y la lista vacía para siempre.
      loadedChats.current = false;
    }
  }, [request]);

  const openChat = useCallback(
    async (peerId: string, peerName: string, peerAvatar: string | null) => {
      setShowPanel(false);

      const existing = windows.find((w) => {
        const chat = chats.find((c) => c.id === w.chatId);
        return chat?.peerId === peerId;
      });

      if (existing) {
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === existing.chatId ? { ...w, status: "expanded" } : w,
          ),
        );
        setChats((prev) =>
          prev.map((c) => (c.id === existing.chatId ? { ...c, unreadCount: 0 } : c)),
        );
        const existingWin = windows.find((w) => w.chatId === existing.chatId);
        if (existingWin) {
          const allIds = existingWin.messages.map((m) => m.id);
          if (allIds.length) {
            send("read", { chatId: existing.chatId, messageIds: allIds });
          }
        }
        return;
      }

      const summary = await request<ChatSummary>("create_direct_chat", { peerId });

      setChats((prev) => {
        const exists = prev.find((c) => c.id === summary.id);
        return exists ? prev : [summary, ...prev];
      });

      const newWindow: ChatWindow = {
        chatId: summary.id,
        title: peerName,
        peerAvatar,
        status: "expanded",
        messages: [],
        loading: true,
        nextCursor: null,
      };

      setWindows((prev) => [...prev, newWindow].slice(-MAX_EXPANDED));

      try {
        const page = await request<MessagesPage>("list_messages", { chatId: summary.id, limit: 50 });
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === summary.id
              ? { ...w, messages: page.items ?? [], nextCursor: page.nextCursor, loading: false }
              : w,
          ),
        );
        const allIds = (page.items ?? []).map((m) => m.id);
        if (allIds.length) {
          send("read", { chatId: summary.id, messageIds: allIds });
        }
        setChats((prev) =>
          prev.map((c) => (c.id === summary.id ? { ...c, unreadCount: 0 } : c)),
        );
      } catch {
        setWindows((prev) =>
          prev.map((w) => (w.chatId === summary.id ? { ...w, loading: false } : w)),
        );
      }
    },
    [request, send, windows, chats],
  );

  const closeWindow = useCallback((chatId: string) => {
    setWindows((prev) => prev.filter((w) => w.chatId !== chatId));
  }, []);

  const minimizeWindow = useCallback((chatId: string) => {
    setWindows((prev) =>
      prev.map((w) => (w.chatId === chatId ? { ...w, status: "minimized" } : w)),
    );
  }, []);

  const expandWindow = useCallback(
    (chatId: string) => {
      const win = windows.find((w) => w.chatId === chatId);
      setWindows((prev) =>
        prev.map((w) => (w.chatId === chatId ? { ...w, status: "expanded" } : w)),
      );
      setChats((prev) =>
        prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
      );
      if (win) {
        const allIds = win.messages.map((m) => m.id);
        if (allIds.length) {
          send("read", { chatId, messageIds: allIds });
        }
      }
    },
    [send, windows],
  );

  const sendMessage = useCallback(
    async (chatId: string, body: string): Promise<boolean> => {
      try {
        const msg = await request<ChatMessage>("send_message", { chatId, body });
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === chatId && !w.messages.some((m) => m.id === msg.id)
              ? { ...w, messages: [...w.messages, msg] }
              : w,
          ),
        );
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId
              ? { ...c, lastMessage: msg.body, lastMessageAt: msg.createdAt }
              : c,
          ),
        );
        return true;
      } catch (err) {
        toastError("No se pudo enviar el mensaje", err instanceof Error ? err.message : undefined);
        return false;
      }
    },
    [request, toastError],
  );

  const loadMoreMessages = useCallback(
    async (chatId: string) => {
      const win = windows.find((w) => w.chatId === chatId);
      if (!win || !win.nextCursor) return;
      const page = await request<MessagesPage>("list_messages", {
        chatId,
        before: win.nextCursor,
        limit: 50,
      });
      setWindows((prev) =>
        prev.map((w) =>
          w.chatId === chatId
            ? { ...w, messages: [...(page.items ?? []), ...w.messages], nextCursor: page.nextCursor }
            : w,
        ),
      );
    },
    [request, windows],
  );

  const openExistingChat = useCallback(
    async (chatId: string, title: string, peerAvatar: string | null) => {
      setShowPanel(false);
      const existingWin = windows.find((w) => w.chatId === chatId);
      if (existingWin) {
        setWindows((prev) =>
          prev.map((w) => (w.chatId === chatId ? { ...w, status: "expanded" } : w)),
        );
        setChats((prev) =>
          prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
        );
        const unread = existingWin.messages.filter((m) => m.status !== "read").map((m) => m.id);
        if (unread.length) {
          send("read", { chatId, messageIds: unread });
        }
        return;
      }
      const newWin: ChatWindow = {
        chatId,
        title,
        peerAvatar,
        status: "expanded",
        messages: [],
        loading: true,
        nextCursor: null,
      };
      setWindows((prev) => [...prev, newWin].slice(-MAX_EXPANDED));
      try {
        const page = await request<MessagesPage>("list_messages", { chatId, limit: 50 });
        const items = page.items ?? [];
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === chatId
              ? { ...w, messages: items, nextCursor: page.nextCursor, loading: false }
              : w,
          ),
        );
        const allIds = items.map((m) => m.id);
        if (allIds.length) {
          send("read", { chatId, messageIds: allIds });
        }
        setChats((prev) =>
          prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
        );
      } catch {
        setWindows((prev) =>
          prev.map((w) => (w.chatId === chatId ? { ...w, loading: false } : w)),
        );
      }
    },
    [request, send, windows],
  );

  const totalUnread = chats.reduce((acc, c) => acc + c.unreadCount, 0);

  return {
    chats,
    windows,
    availableUsers,
    showPanel,
    totalUnread,
    setShowPanel,
    loadAvailableUsers,
    loadChats,
    openChat,
    openExistingChat,
    closeWindow,
    minimizeWindow,
    expandWindow,
    sendMessage,
    loadMoreMessages,
  };
};
