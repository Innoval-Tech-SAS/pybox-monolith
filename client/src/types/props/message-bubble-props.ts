import type { MessageStatus } from "@/types/chat/chat-types";

export interface MessageStatusIconProps {
  status: MessageStatus;
}

export interface MessageBubbleProps {
  /** Contenido del mensaje. */
  body: string;
  /** Hora/fecha ya formateada para mostrar (el formateo queda a cargo del caller). */
  timestamp: string;
  /** true si el mensaje lo envió el usuario actual. */
  isOwn: boolean;
  /** Nombre del remitente — se muestra solo si viene y el mensaje no es propio (chats grupales/widget). */
  senderName?: string;
  /** Estado de entrega — se muestra solo si viene y el mensaje es propio (chats internos, no aplica a WhatsApp). */
  status?: MessageStatus;
  /** Ancho máximo de la burbuja; por defecto 60% (vista principal de chat-page). Los contextos angostos (widget flotante) pueden pasar un valor mayor. */
  maxWidthClassName?: string;
}
