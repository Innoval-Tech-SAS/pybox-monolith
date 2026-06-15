import type { ChatMessage, ChatWindow as ChatWindowType } from "@/chat/types/chat/chat-types";

export interface ChatWindowProps {
  window: ChatWindowType;
  currentUserId: number;
  onClose: () => void;
  onMinimize: () => void;
  onSend: (body: string) => void;
  onLoadMore: () => void;
}
