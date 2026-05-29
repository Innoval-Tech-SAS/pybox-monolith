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
          send("read", { chatId: msg.chatId, messageIds: [msg.id] });
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

  const { send, request } = useChatWebSocket(handleWsEvent);

  const loadChats = useCallback(async () => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    setChatsLoading(true);
    try {
      const data = await request<ChatSummary[]>("list_chats", {});
      setChats(data ?? []);
    } finally {
      setChatsLoading(false);
    }
  }, [request]);

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
        const page = await request<MessagesPage>("list_messages", { chatId, limit: 50 });
        const items = page.items ?? [];
        setSelected({ chatId, messages: items, loading: false, nextCursor: page.nextCursor });
        const allIds = items.map((m) => m.id);
        if (allIds.length) {
          send("read", { chatId, messageIds: allIds });
        }
      } catch {
        setSelected((prev) => (prev ? { ...prev, loading: false } : null));
      }
    },
    [request, send],
  );

  const loadMore = useCallback(async () => {
    if (!selected?.nextCursor || selected.loading) return;
    const { chatId, nextCursor } = selected;
    setSelected((prev) => (prev ? { ...prev, loading: true } : null));
    try {
      const page = await request<MessagesPage>("list_messages", {
        chatId,
        before: nextCursor,
        limit: 50,
      });
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
  }, [request, selected]);

  const sendMessage = useCallback(
    async (body: string) => {
      if (!selected) return;
      const msg = await request<ChatMessage>("send_message", { chatId: selected.chatId, body });
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
    [request, selected],
  );

  const openNewChat = useCallback(
    async (peerId: number, peerName: string, peerAvatar: string | null) => {
      setShowNewChat(false);
      const summary = await request<ChatSummary>("create_direct_chat", { peerId });
      setChats((prev) => {
        const exists = prev.find((c) => c.id === summary.id);
        return exists ? prev : [summary, ...prev];
      });
      await selectChat(summary.id);
    },
    [request, selectChat],
  );

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
