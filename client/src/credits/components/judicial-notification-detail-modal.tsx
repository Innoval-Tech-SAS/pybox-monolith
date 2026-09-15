import { Modal } from "@/ui/components/modal/modal";
import { Badge } from "@/ui/components/badge";
import { JUDICIAL_PRIORITY_BADGE_COLOR } from "@/constants/credits/judicial-priority";
import { formatPaymentDate } from "@/credits/utils/financial-calendar-utils";
import { JudicialAttachmentList } from "./judicial-attachment-list";
import type { JudicialNotification } from "@/credits/types/judicial-types";

interface JudicialNotificationDetailModalProps {
  notification: JudicialNotification | null;
  isOpen: boolean;
  onClose: () => void;
  priorityLabels: Record<string, string>;
}

/** Detalle de una notificación judicial: cuerpo completo y adjuntos descargables.
 * Se usa tanto en el buzón del titular como en el panel de la entidad. */
export const JudicialNotificationDetailModal: React.FC<JudicialNotificationDetailModalProps> = ({
  notification,
  isOpen,
  onClose,
  priorityLabels,
}) => {
  if (!notification) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-lg p-6 lg:p-8">
      <div className="flex items-start justify-between gap-3 pr-8">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">{notification.title}</h3>
        <Badge
          variant="light"
          color={JUDICIAL_PRIORITY_BADGE_COLOR[notification.priority] ?? "light"}
          size="sm"
        >
          {priorityLabels[notification.priority] ?? notification.priority}
        </Badge>
      </div>
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {notification.entityName} · Crédito #{notification.creditNumber} ·{" "}
        {formatPaymentDate(notification.notifiedAt)}
      </p>

      <p className="mt-4 text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">{notification.body}</p>

      <div className="mt-6">
        <p className="mb-3 text-xs font-semibold tracking-wide text-gray-400 uppercase dark:text-gray-500">
          Adjuntos
          {notification.attachments.length > 0 && (
            <span className="ml-2 font-normal text-gray-500 normal-case">
              ({notification.attachments.length})
            </span>
          )}
        </p>
        <JudicialAttachmentList attachments={notification.attachments} />
      </div>
    </Modal>
  );
};
