import React, { KeyboardEvent, useEffect, useRef, useState } from "react";
import { MessageSquare } from "lucide-react";
import { useChatPage } from "../hooks/use-chat-page";
import { useAuth } from "../../hooks/use-auth";
import type { ChatMessage } from "../../types/chat/chat-types";
import EmptyState from "@/ui/components/common/empty-state";

const StatusIcon: React.FC<{ status: ChatMessage["status"] }> = ({ status }) => {
  if (status === "read") return <span className="text-brand-500 text-[10px]">✓✓</span>;
  if (status === "delivered") return <span className="text-gray-400 text-[10px]">✓✓</span>;
  return <span className="text-gray-400 text-[10px]">✓</span>;
};

export const ChatPage: React.FC = () => {
  const {
    chats,
    chatsLoading,
    selected,
    availableUsers,
    showNewChat,
    setShowNewChat,
    selectChat,
    loadMore,
    sendMessage,
    openNewChat,
    loadAvailableUsers,
  } = useChatPage();

  const { getSession } = useAuth();
  const currentUserId = getSession()?.user_id ?? 0;

  const [input, setInput] = useState("");
  const [search, setSearch] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [selected?.messages.length]);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (el && el.scrollTop === 0 && selected?.nextCursor) {
      loadMore();
    }
  };

  const submit = () => {
    const trimmed = input.trim();
    if (!trimmed || !selected) return;
    sendMessage(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const filteredChats = chats.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase()),
  );

  const selectedSummary = chats.find((c) => c.id === selected?.chatId);

  return (
    <div className="flex h-[calc(100vh-174px)] gap-5 overflow-hidden">
      {/* Sidebar */}
      <div className="flex flex-col w-80 shrink-0 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-dark overflow-hidden">
        {/* Sidebar header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">Chats</h2>
          <button
            onClick={() => {
              setShowNewChat(true);
              loadAvailableUsers();
            }}
            className="w-8 h-8 rounded-full bg-brand-500 text-white flex items-center justify-center hover:bg-brand-600 transition-colors text-lg leading-none"
            title="Nuevo chat"
          >
            +
          </button>
        </div>

        {/* Search */}
        <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-800">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar..."
            className="w-full bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-1.5 text-sm text-gray-800 dark:text-white/90 placeholder:text-gray-400 focus:outline-none"
          />
        </div>

        {/* New chat panel */}
        {showNewChat && (
          <div className="border-b border-gray-200 dark:border-gray-800 px-4 py-2 max-h-48 overflow-y-auto custom-scrollbar">
            {availableUsers.length === 0 ? (
              <p className="text-xs text-gray-400 py-2">Sin usuarios disponibles</p>
            ) : (
              availableUsers.map((u) => (
                <button
                  key={u.id}
                  onClick={() => openNewChat(u.id, u.fullName, u.profilePhotoUrl)}
                  className="flex items-center gap-2 w-full py-1.5 hover:bg-gray-50 dark:hover:bg-white/5 rounded-lg px-2 text-left transition-colors"
                >
                  {u.profilePhotoUrl ? (
                    <img src={u.profilePhotoUrl} alt={u.fullName} className="w-8 h-8 rounded-full object-cover shrink-0" />
                  ) : (
                    <span className="w-8 h-8 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center shrink-0">
                      {u.fullName.charAt(0).toUpperCase()}
                    </span>
                  )}
                  <span className="text-sm text-gray-800 dark:text-white/90 truncate">{u.fullName}</span>
                </button>
              ))
            )}
          </div>
        )}

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {chatsLoading ? (
            <p className="text-center text-xs text-gray-400 mt-6">Cargando...</p>
          ) : filteredChats.length === 0 ? (
            <p className="text-center text-xs text-gray-400 mt-6">Sin conversaciones</p>
          ) : (
            filteredChats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => selectChat(chat.id)}
                className={`flex items-center gap-3 w-full px-4 py-3 text-left border-b border-gray-200 dark:border-gray-800 transition-colors ${
                  selected?.chatId === chat.id
                    ? "bg-brand-50 dark:bg-brand-500/10"
                    : "hover:bg-gray-50 dark:hover:bg-white/5"
                }`}
              >
                {chat.peerAvatar ? (
                  <img src={chat.peerAvatar} alt={chat.title} className="w-10 h-10 rounded-full object-cover shrink-0" />
                ) : (
                  <span className="w-10 h-10 rounded-full bg-brand-500 text-white text-sm font-semibold flex items-center justify-center shrink-0">
                    {chat.title.charAt(0).toUpperCase()}
                  </span>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800 dark:text-white/90 truncate">{chat.title}</span>
                    {chat.unreadCount > 0 && (
                      <span className="ml-1 shrink-0 min-w-4.5 h-4.5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1">
                        {chat.unreadCount > 99 ? "99+" : chat.unreadCount}
                      </span>
                    )}
                  </div>
                  {chat.lastMessage && (
                    <p className="text-xs text-gray-400 truncate mt-0.5">{chat.lastMessage}</p>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Chat panel */}
      <div className="flex flex-col flex-1 min-w-0 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-dark overflow-hidden">
        {!selected ? (
          <div className="flex-1 flex items-center justify-center">
            <EmptyState icon={MessageSquare} title="Selecciona una conversación" />
          </div>
        ) : (
          <>
            {/* Panel header */}
            <div className="flex items-center gap-3 px-5 py-3 border-b border-gray-200 dark:border-gray-800">
              {selectedSummary?.peerAvatar ? (
                <img src={selectedSummary.peerAvatar} alt={selectedSummary.title} className="w-9 h-9 rounded-full object-cover" />
              ) : (
                <span className="w-9 h-9 rounded-full bg-brand-500 text-white text-sm font-semibold flex items-center justify-center">
                  {(selectedSummary?.title ?? "?").charAt(0).toUpperCase()}
                </span>
              )}
              <span className="text-sm font-semibold text-gray-800 dark:text-white/90">
                {selectedSummary?.title ?? ""}
              </span>
            </div>

            {/* Messages */}
            <div
              ref={scrollRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto custom-scrollbar px-5 py-4 flex flex-col gap-3"
            >
              {selected.loading && (
                <p className="text-center text-xs text-gray-400">Cargando...</p>
              )}
              {selected.nextCursor && !selected.loading && (
                <button
                  onClick={loadMore}
                  className="text-xs text-brand-500 hover:underline self-center"
                >
                  Cargar más
                </button>
              )}
              {selected.messages.map((msg) => {
                const isOwn = msg.senderId === currentUserId;
                return (
                  <div key={msg.id} className={`flex flex-col ${isOwn ? "items-end" : "items-start"}`}>
                    {!isOwn && (
                      <span className="text-[11px] text-gray-400 mb-0.5 px-1">{msg.senderName}</span>
                    )}
                    <div
                      className={`max-w-[60%] px-4 py-2 text-sm wrap-break-word rounded-2xl ${
                        isOwn
                          ? "bg-brand-500 text-white rounded-tr-sm"
                          : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white/90 rounded-tl-sm"
                      }`}
                    >
                      {msg.body}
                    </div>
                    <div className="flex items-center gap-1 mt-1 px-1">
                      <span className="text-[11px] text-gray-400">
                        {new Date(msg.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      {isOwn && <StatusIcon status={msg.status} />}
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex items-end gap-3 px-5 py-3 border-t border-gray-200 dark:border-gray-800">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje..."
                rows={1}
                className="flex-1 resize-none bg-gray-50 dark:bg-gray-900 rounded-xl px-4 py-2 text-sm text-gray-800 dark:text-white/90 placeholder:text-gray-400 focus:outline-none max-h-28 overflow-y-auto custom-scrollbar"
              />
              <button
                onClick={submit}
                disabled={!input.trim()}
                className="shrink-0 w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                </svg>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
