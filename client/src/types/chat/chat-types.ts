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

export const CHAT_TYPE_DIRECT = 0;
export const CHAT_TYPE_GROUP = 1;

export const CHAT_MEMBER_ROLE_MEMBER = 0;
export const CHAT_MEMBER_ROLE_ADMIN = 1;
export const CHAT_MEMBER_ROLE_OWNER = 2;

export interface ChatSummary {
  id: string;
  type: number;
  title: string;
  peerId: string | null;
  peerAvatar: string | null;
  memberCount: number;
  lastMessage: string | null;
  lastMessageAt: string | null;
  unreadCount: number;
}

export interface ChatMember {
  userId: string;
  fullName: string;
  profilePhotoUrl: string | null;
  role: number;
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
  | { event: "group_members"; data: { chatId: string; members: ChatMember[] } }
  | { event: "group_updated"; data: { chatId: string; memberCount: number } }
  | { event: "member_removed"; data: { chatId: string; userId: string } }
  | { event: "error"; data: { detail: string } };
