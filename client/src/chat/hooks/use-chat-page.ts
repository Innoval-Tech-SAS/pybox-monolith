import { useCallback, useEffect, useRef, useState } from "react";
import { useApiClient } from "../../hooks/use-api-client";
import { playMessageSound } from "../utils/chat-sound";
import type {
  ChatAvailableUser,
  ChatMessage,
  ChatSummary,
  MessagesPage,
  WsChatEvent,
} from "../../types/chat/chat-types";
import { useChatWebSocket } from "./use-chat-websocket";

interface ConversationState {
  chatId: string;
  messages: ChatMessage[];
  loading: boolean;
  nextCursor: string | null;
}

export const useChatPage = () => {
  const { apiClient } = useApiClient();
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [chatsLoading, setChatsLoading] = useState(true);
  const [selected, setSelected] = useState<ConversationState | null>(null);
  const [availableUsers, setAvailableUsers] = useState<ChatAvailableUser[]>([]);
  const [showNewChat, setShowNewChat] = useState(false);
  const loadedRef = useRef(false);

  const loadChats = useCallback(async () => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    setChatsLoading(true);
    try {
      const data: ChatSummary[] = await apiClient("/chats");
      setChats(data ?? []);
    } finally {
      setChatsLoading(false);
    }
  }, [apiClient]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  const selectChat = useCallback(
    async (chatId: string) => {
      setSelected({ chatId, messages: [], loading: true, nextCursor: null });
      setChats((prev) =>
        prev.map((c) => (c.id === chatId ? { ...c, unreadCount: 0 } : c)),
      );
      try {
        const page: MessagesPage = await apiClient(
          `/chats/${chatId}/messages?limit=50`,
        );
        const items = page.items ?? [];
        setSelected({ chatId, messages: items, loading: false, nextCursor: page.nextCursor });

        const allIds = items.map((m) => m.id);
        if (allIds.length) {
          await apiClient(`/chats/${chatId}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: allIds }),
          });
        }
      } catch {
        setSelected((prev) => (prev ? { ...prev, loading: false } : null));
      }
    },
    [apiClient],
  );

  const loadMore = useCallback(async () => {
    if (!selected?.nextCursor || selected.loading) return;
    const { chatId, nextCursor } = selected;
    setSelected((prev) => (prev ? { ...prev, loading: true } : null));
    try {
      const page: MessagesPage = await apiClient(
        `/chats/${chatId}/messages?limit=50&before=${encodeURIComponent(nextCursor)}`,
      );
      setSelected((prev) =>
        prev
          ? {
              ...prev,
              messages: [...(page.items ?? []), ...prev.messages],
              nextCursor: page.nextCursor,
              loading: false,
            }
          : null,
      );
    } catch {
      setSelected((prev) => (prev ? { ...prev, loading: false } : null));
    }
  }, [apiClient, selected]);

  const sendMessage = useCallback(
    async (body: string) => {
      if (!selected) return;
      const msg: ChatMessage = await apiClient(
        `/chats/${selected.chatId}/messages`,
        { method: "POST", body: JSON.stringify({ body }) },
      );
      setSelected((prev) =>
        prev && !prev.messages.some((m) => m.id === msg.id)
          ? { ...prev, messages: [...prev.messages, msg] }
          : prev,
      );
      setChats((prev) =>
        prev.map((c) =>
          c.id === selected.chatId
            ? { ...c, lastMessage: msg.body, lastMessageAt: msg.createdAt }
            : c,
        ),
      );
    },
    [apiClient, selected],
  );

  const openNewChat = useCallback(
    async (peerId: number, peerName: string, peerAvatar: string | null) => {
      setShowNewChat(false);
      const summary: ChatSummary = await apiClient("/chats/direct", {
        method: "POST",
        body: JSON.stringify({ peerId }),
      });
      setChats((prev) => {
        const exists = prev.find((c) => c.id === summary.id);
        return exists ? prev : [summary, ...prev];
      });
      await selectChat(summary.id);
    },
    [apiClient, selectChat],
  );

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
        const isSelected = selected?.chatId === msg.chatId;
        setSelected((prev) =>
          prev?.chatId === msg.chatId && !prev.messages.some((m) => m.id === msg.id)
            ? { ...prev, messages: [...prev.messages, msg] }
            : prev,
        );
        setChats((prev) =>
          prev.map((c) =>
            c.id === msg.chatId
              ? {
                  ...c,
                  lastMessage: msg.body,
                  lastMessageAt: msg.createdAt,
                  unreadCount: isSelected ? 0 : c.unreadCount + 1,
                }
              : c,
          ),
        );
        if (isSelected) {
          apiClient(`/chats/${msg.chatId}/read`, {
            method: "POST",
            body: JSON.stringify({ messageIds: [msg.id] }),
          }).catch(() => {});
        }
      } else if (event.event === "read") {
        const { chatId, messageIds } = event.data;
        setSelected((prev) =>
          prev?.chatId === chatId
            ? {
                ...prev,
                messages: prev.messages.map((m) =>
                  messageIds.includes(m.id) ? { ...m, status: "read" as const } : m,
                ),
              }
            : prev,
        );
      }
    },
    [selected?.chatId],
  );

  useChatWebSocket(handleWsEvent);

  const totalUnread = chats.reduce((acc, c) => acc + c.unreadCount, 0);

  return {
    chats,
    chatsLoading,
    selected,
    availableUsers,
    showNewChat,
    totalUnread,
    setShowNewChat,
    selectChat,
    loadMore,
    sendMessage,
    openNewChat,
    loadAvailableUsers,
  };
};
