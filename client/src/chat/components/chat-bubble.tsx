import React from "react";
import type { ChatBubbleProps } from "@/chat/types/chat-bubble-props";

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  window,
  unreadCount,
  onExpand,
  onClose,
}) => {
  return (
    <div className="group relative flex flex-col items-center">
      <button
        onClick={onExpand}
        className="relative w-12 h-12 rounded-full shadow-md overflow-hidden border-2 border-white dark:border-boxdark focus:outline-none hover:scale-105 transition-transform"
        title={window.title}
      >
        {window.peerAvatar ? (
          <img
            src={window.peerAvatar}
            alt={window.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="w-full h-full flex items-center justify-center bg-brand-500 text-white text-sm font-semibold">
            {window.title.charAt(0).toUpperCase()}
          </span>
        )}

        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-4.5 h-4.5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1 leading-none">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      <button
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
        className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-gray-500 text-white text-[10px] items-center justify-center hidden group-hover:flex hover:bg-gray-700 transition-colors"
        title="Cerrar"
      >
        ✕
      </button>

      <span className="mt-1 text-[10px] text-gray-500 dark:text-gray-400 max-w-13 truncate text-center leading-none">
        {window.title.split(" ")[0]}
      </span>
    </div>
  );
};
