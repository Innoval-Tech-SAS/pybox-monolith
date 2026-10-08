import type { ChatWindow } from "@/types/chat/chat-types";

export interface ChatBubbleProps {
  window: ChatWindow;
  unreadCount: number;
  onExpand: () => void;
  onClose: () => void;
}
