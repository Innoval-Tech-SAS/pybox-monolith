import type { ChatAvailableUser, ChatSummary } from "@/types/chat/chat-types";

export interface AvailableUsersPanelProps {
  users: ChatAvailableUser[];
  chats: ChatSummary[];
  onSelect: (user: ChatAvailableUser) => void;
  onOpenChat: (chatId: string, title: string, peerAvatar: string | null) => void;
  onClose: () => void;
}
