import type { JudicialNotification } from "@/credits/types/judicial-types";
import type { ObligationRow, ObligationsSummary } from "@/credits/types/obligations-types";

export interface SelfHomeHeaderProps {
  firstName: string;
  unreadCount: number;
  onOpenInbox: () => void;
}

export interface ObligationsSummaryCardsProps {
  summary: ObligationsSummary;
  loading?: boolean;
}

export interface ObligationsTableProps {
  rows: ObligationRow[];
  /** Etiquetas servidas por GET /credits/types. */
  creditTypeLabels: Record<string, string>;
  /** Etiquetas servidas por GET /payments/statuses. */
  paymentStatusLabels: Record<string, string>;
  loading?: boolean;
}

export interface JudicialInboxPanelProps {
  items: JudicialNotification[];
  unreadCount: number;
  /** Etiquetas servidas por GET /judicial-notifications/priorities. */
  priorityLabels: Record<string, string>;
  loading?: boolean;
  onRead: (notificationId: string) => void;
}
