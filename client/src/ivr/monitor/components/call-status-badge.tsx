import { CALL_STATUS_CLASSES, CALL_STATUS_LABELS, LIVE_CALL_STATUSES } from "../constants/call-status-labels";
import type { IvrCallStatus } from "../types/ivr-monitor-types";

interface CallStatusBadgeProps {
  status: IvrCallStatus;
}

export const CallStatusBadge: React.FC<CallStatusBadgeProps> = ({ status }) => {
  const isLive = LIVE_CALL_STATUSES.includes(status);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${CALL_STATUS_CLASSES[status]}`}
    >
      {isLive && (
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-60" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-current" />
        </span>
      )}
      {CALL_STATUS_LABELS[status]}
    </span>
  );
};
