/**
 * Buzón judicial del titular. Vive en `credits/` porque la notificación cuelga de un
 * crédito: el backend la sirve con el crédito y la entidad ya resueltos.
 */

export interface JudicialNotificationAttachment {
  id: string;
  name: string;
  url: string;
  size: number;
}

export interface JudicialNotification {
  id: string;
  title: string;
  body: string;
  /** Código de prioridad (urgente, media, baja, informativa). */
  priority: string;
  isRead: boolean;
  notifiedAt: string;
  creditId: string;
  creditNumber: string;
  creditType: string;
  entityName: string;
  attachments: JudicialNotificationAttachment[];
}

export interface JudicialInbox {
  items: JudicialNotification[];
  unreadCount: number;
}

/** Opción servida por GET /judicial-notifications/priorities. */
export interface JudicialPriorityOption {
  value: string;
  label: string;
}

/** Payload de POST /judicial-notifications, emitido desde el panel de la entidad. */
export interface JudicialNotificationCreatePayload {
  creditId: string;
  title: string;
  body: string;
  priority: string;
  notifiedAt?: string;
}
