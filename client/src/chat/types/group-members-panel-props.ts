import type { ChatAvailableUser, ChatMember } from "@/types/chat/chat-types";

export type GroupMembersPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  members: ChatMember[];
  availableUsers: ChatAvailableUser[];
  currentUserId: string;
  onAddMember: (userId: string) => Promise<void>;
  onRemoveMember: (userId: string) => Promise<void>;
};
