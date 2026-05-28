import React, { KeyboardEvent, useEffect, useRef, useState } from "react";
import type { ChatMessage, ChatWindow as ChatWindowType } from "../../types/chat/chat-types";

interface ChatWindowProps {
  window: ChatWindowType;
  currentUserId: number;
  onClose: () => void;
  onMinimize: () => void;
  onSend: (body: string) => void;
  onLoadMore: () => void;
}

const StatusIcon: React.FC<{ status: ChatMessage["status"] }> = ({ status }) => {
  if (status === "read")
    return <span className="text-brand-500 text-[10px]">✓✓</span>;
  if (status === "delivered")
    return <span className="text-gray-400 text-[10px]">✓✓</span>;
  return <span className="text-gray-400 text-[10px]">✓</span>;
};

export const ChatWindow: React.FC<ChatWindowProps> = ({
  window: win,
  currentUserId,
  onClose,
  onMinimize,
  onSend,
  onLoadMore,
}) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [win.messages.length]);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (el && el.scrollTop === 0 && win.nextCursor) {
      onLoadMore();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const submit = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setInput("");
  };

  return (
    <div className="flex flex-col w-72 h-[420px] rounded-t-xl bg-white dark:bg-gray-dark shadow-xl border border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 dark:border-gray-800 rounded-t-xl">
        <div className="relative flex-shrink-0">
          {win.peerAvatar ? (
            <img
              src={win.peerAvatar}
              alt={win.title}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <span className="w-8 h-8 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center">
              {win.title.charAt(0).toUpperCase()}
            </span>
          )}
        </div>
        <span className="flex-1 text-sm font-medium text-gray-800 dark:text-white/90 truncate">
          {win.title}
        </span>
        <button
          onClick={onMinimize}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-white/70 px-1 text-base leading-none"
          title="Minimizar"
        >
          –
        </button>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-white/70 px-1 text-base leading-none"
          title="Cerrar"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto custom-scrollbar px-3 py-2 flex flex-col gap-2"
      >
        {win.loading && (
          <p className="text-center text-xs text-gray-400 mt-4">Cargando...</p>
        )}
        {win.nextCursor && !win.loading && (
          <button
            onClick={onLoadMore}
            className="text-xs text-brand-500 hover:underline self-center"
          >
            Cargar más
          </button>
        )}
        {win.messages.map((msg) => {
          const isOwn = msg.senderId === currentUserId;
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isOwn ? "items-end" : "items-start"}`}
            >
              {!isOwn && (
                <span className="text-[10px] text-gray-400 mb-0.5 px-1">
                  {msg.senderName}
                </span>
              )}
              <div
                className={`max-w-[85%] px-3 py-1.5 text-sm break-words ${
                  isOwn
                    ? "bg-brand-500 text-white rounded-t-xl rounded-bl-xl"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white/90 rounded-t-xl rounded-br-xl"
                }`}
              >
                {msg.body}
              </div>
              <div className="flex items-center gap-1 mt-0.5 px-1">
                <span className="text-[10px] text-gray-400">
                  {new Date(msg.createdAt).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                {isOwn && <StatusIcon status={msg.status} />}
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex items-end gap-2 px-3 py-2 border-t border-gray-200 dark:border-gray-800">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un mensaje..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-800 dark:text-white/90 placeholder:text-gray-400 dark:placeholder:text-white/30 focus:outline-none py-1 max-h-20 overflow-y-auto custom-scrollbar"
        />
        <button
          onClick={submit}
          disabled={!input.trim()}
          className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-500 text-white flex items-center justify-center hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          title="Enviar"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-4 h-4"
          >
            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
          </svg>
        </button>
      </div>
    </div>
  );
};
