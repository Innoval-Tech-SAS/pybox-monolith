import type { ChatAvailableUser } from "@/types/chat/chat-types";

export type NewGroupModalProps = {
  isOpen: boolean;
  onClose: () => void;
  availableUsers: ChatAvailableUser[];
  onCreate: (title: string, memberIds: string[]) => Promise<void>;
};
