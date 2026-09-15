export type MessageStatus = "sent" | "delivered" | "read";

export interface ChatAvailableUser {
  id: string;
  fullName: string;
  profilePhotoUrl: string | null;
  isOnline: boolean;
}

export interface ChatMessage {
  id: string;
  chatId: string;
  senderId: string;
  senderName: string;
  senderAvatar: string | null;
  body: string;
  createdAt: string;
  status: MessageStatus;
}

export interface ChatSummary {
  id: string;
  type: number;
  title: string;
  peerId: string | null;
  peerAvatar: string | null;
  lastMessage: string | null;
  lastMessageAt: string | null;
  unreadCount: number;
}

export interface MessagesPage {
  items: ChatMessage[];
  nextCursor: string | null;
}

export interface ChatWindow {
  chatId: string;
  title: string;
  peerAvatar: string | null;
  status: "expanded" | "minimized";
  messages: ChatMessage[];
  loading: boolean;
  nextCursor: string | null;
}

export type WsChatEvent =
  | { event: "message"; data: ChatMessage }
  | { event: "read"; data: { chatId: string; messageIds: string[]; readerId: string } }
  | { event: "chats"; data: ChatSummary[] }
  | { event: "chat"; data: ChatSummary }
  | { event: "messages"; data: MessagesPage }
  | { event: "error"; data: { detail: string } };
