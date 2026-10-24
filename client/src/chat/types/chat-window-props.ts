import type { ChatWindow as ChatWindowType } from "@/types/chat/chat-types";

export interface ChatWindowProps {
  window: ChatWindowType;
  currentUserId: string;
  onClose: () => void;
  onMinimize: () => void;
  /** Devuelve `true` si el mensaje se envió con éxito -- el input solo se limpia en ese caso. */
  onSend: (body: string) => Promise<boolean>;
  onLoadMore: () => void;
}
