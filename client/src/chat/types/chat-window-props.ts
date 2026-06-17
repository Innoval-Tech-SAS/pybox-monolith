import type { ChatMessage, ChatWindow as ChatWindowType } from "@/types/chat/chat-types";

export interface ChatWindowProps {
  window: ChatWindowType;
  currentUserId: string;
  onClose: () => void;
  onMinimize: () => void;
  onSend: (body: string) => void;
  onLoadMore: () => void;
}
