import type { ChatWindow } from "@/chat/types/chat/chat-types";

export interface ChatBubbleProps {
  window: ChatWindow;
  unreadCount: number;
  onExpand: () => void;
  onClose: () => void;
}
