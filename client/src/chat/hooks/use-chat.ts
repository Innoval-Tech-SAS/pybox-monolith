import { useCallback, useRef, useState } from "react";
import { useApiClient } from "../../hooks/use-api-client";
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

  const loadChats = useCallback(async () => {
    if (loadedChats.current) return;
    loadedChats.current = true;
    try {
      const data: ChatSummary[] = await apiClient("/chats");
      setChats(data ?? []);
    } catch {
      // silent
    }
  }, [apiClient]);

  const openChat = useCallback(
    async (peerId: number, peerName: string, peerAvatar: string | null) => {
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
          const unread = existingWin.messages.filter((m) => m.status !== "read").map((m) => m.id);
          if (unread.length) {
            apiClient(`/chats/${existing.chatId}/read`, {
              method: "POST",
              body: JSON.stringify({ messageIds: unread }),
            }).catch(() => {});
          }
        }
        return;
      }

      const summary: ChatSummary = await apiClient("/chats/direct", {
        method: "POST",
        body: JSON.stringify({ peerId }),
      });

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

      setWindows((prev) => {
        const updated = [...prev, newWindow];
        return updated.slice(-MAX_EXPANDED);
      });

      try {
        const page: MessagesPage = await apiClient(
          `/chats/${summary.id}/messages?limit=50`,
        );
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === summary.id
              ? {
                  ...w,
                  messages: page.items ?? [],
                  nextCursor: page.nextCursor,
                  loading: false,
                }
              : w,
          ),
        );

        const unread = (page.items ?? [])
          .filter((m) => m.status !== "read")
          .map((m) => m.id);
        if (unread.length) {
          await apiClient(`/chats/${summary.id}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: unread }),
          });
          setChats((prev) =>
            prev.map((c) =>
              c.id === summary.id ? { ...c, unreadCount: 0 } : c,
            ),
          );
        }
      } catch {
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === summary.id ? { ...w, loading: false } : w,
          ),
        );
      }
    },
    [apiClient, windows, chats],
  );

  const closeWindow = useCallback((chatId: string) => {
    setWindows((prev) => prev.filter((w) => w.chatId !== chatId));
  }, []);

  const minimizeWindow = useCallback((chatId: string) => {
    setWindows((prev) =>
      prev.map((w) =>
        w.chatId === chatId ? { ...w, status: "minimized" } : w,
      ),
    );
  }, []);

  const expandWindow = useCallback((chatId: string) => {
    const win = windows.find((w) => w.chatId === chatId);
    setWindows((prev) =>
      prev.map((w) => (w.chatId === chatId ? { ...w, status: "expanded" } : w)),
    );
    setChats((prev) =>
      prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
    );
    if (win) {
      const unread = win.messages.filter((m) => m.status !== "read").map((m) => m.id);
      if (unread.length) {
        apiClient(`/chats/${chatId}/read`, {
          method: "POST",
          body: JSON.stringify({ messageIds: unread }),
        }).catch(() => {});
      }
    }
  }, [apiClient, windows]);

  const sendMessage = useCallback(
    async (chatId: string, body: string) => {
      const msg: ChatMessage = await apiClient(`/chats/${chatId}/messages`, {
        method: "POST",
        body: JSON.stringify({ body }),
      });

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
    },
    [apiClient],
  );

  const loadMoreMessages = useCallback(
    async (chatId: string) => {
      const win = windows.find((w) => w.chatId === chatId);
      if (!win || !win.nextCursor) return;

      const page: MessagesPage = await apiClient(
        `/chats/${chatId}/messages?limit=50&before=${encodeURIComponent(win.nextCursor)}`,
      );

      setWindows((prev) =>
        prev.map((w) =>
          w.chatId === chatId
            ? {
                ...w,
                messages: [...(page.items ?? []), ...w.messages],
                nextCursor: page.nextCursor,
              }
            : w,
        ),
      );
    },
    [apiClient, windows],
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
          apiClient(`/chats/${chatId}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: unread }),
          }).catch(() => {});
        }
        return;
      }
      const newWin: ChatWindow = { chatId, title, peerAvatar, status: "expanded", messages: [], loading: true, nextCursor: null };
      setWindows((prev) => [...prev, newWin].slice(-MAX_EXPANDED));
      try {
        const page: MessagesPage = await apiClient(`/chats/${chatId}/messages?limit=50`);
        const items = page.items ?? [];
        setWindows((prev) =>
          prev.map((w) => (w.chatId === chatId ? { ...w, messages: items, nextCursor: page.nextCursor, loading: false } : w)),
        );
        const unread = items.filter((m) => m.status !== "read").map((m) => m.id);
        setChats((prev) =>
          prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
        );
        if (unread.length) {
          apiClient(`/chats/${chatId}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: unread }),
          }).catch(() => {});
        }
      } catch {
        setWindows((prev) =>
          prev.map((w) => (w.chatId === chatId ? { ...w, loading: false } : w)),
        );
      }
    },
    [apiClient, windows],
  );

  const handleWsEvent = useCallback(
    (event: WsChatEvent) => {
      if (event.event === "message") {
        const msg = event.data;
        playMessageSound();
        const winExpanded = windows.find((w) => w.chatId === msg.chatId)?.status === "expanded";
        setWindows((prev) =>
          prev.map((w) =>
            w.chatId === msg.chatId && !w.messages.some((m) => m.id === msg.id)
              ? { ...w, messages: [...w.messages, msg] }
              : w,
          ),
        );
        setChats((prev) =>
          prev.map((c) =>
            c.id === msg.chatId
              ? {
                  ...c,
                  lastMessage: msg.body,
                  lastMessageAt: msg.createdAt,
                  unreadCount: winExpanded ? c.unreadCount : c.unreadCount + 1,
                }
              : c,
          ),
        );
        if (winExpanded) {
          apiClient(`/chats/${msg.chatId}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: [msg.id] }),
          }).catch(() => {});
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
    [windows],
  );

  useChatWebSocket(handleWsEvent);

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
