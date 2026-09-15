import React from "react";
import type { MessageBubbleProps } from "@/types/props/message-bubble-props";
import { StatusIcon } from "./message-status-icon";

/**
 * Burbuja de mensaje compartida entre chat-page, el widget flotante (chat-window) y
 * whatsapp-chats-page. Variante visual única: rounded-2xl con esquina recortada del
 * lado del remitente (rounded-tr-sm propio / rounded-tl-sm ajeno), tomada de chat-page.tsx.
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  body,
  timestamp,
  isOwn,
  senderName,
  status,
  maxWidthClassName = "max-w-[60%]",
}) => {
  return (
    <div className={`flex flex-col ${isOwn ? "items-end" : "items-start"}`}>
      {!isOwn && senderName && (
        <span className="text-theme-xs text-gray-400 mb-0.5 px-1">{senderName}</span>
      )}
      <div
        className={`${maxWidthClassName} px-4 py-2 text-sm wrap-break-word rounded-2xl ${
          isOwn
            ? "bg-brand-500 text-white rounded-tr-sm"
            : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white/90 rounded-tl-sm"
        }`}
      >
        {body}
      </div>
      <div className="flex items-center gap-1 mt-1 px-1">
        <span className="text-theme-xs text-gray-400">{timestamp}</span>
        {isOwn && status && <StatusIcon status={status} />}
      </div>
    </div>
  );
};
