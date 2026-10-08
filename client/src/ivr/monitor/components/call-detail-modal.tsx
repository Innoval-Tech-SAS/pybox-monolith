import { Modal } from "@/ui/components/modal/modal";
import { CallStatusBadge } from "./call-status-badge";
import { AMD_LABELS, DIAL_STATUS_LABELS } from "../constants/call-status-labels";
import type { CallEntry } from "../hooks/use-call-monitor";

const formatTime = (iso: string | null): string => {
  if (!iso) return "—";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString();
};

const Field: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div>
    <p className="text-xs text-gray-400 dark:text-gray-500">{label}</p>
    <div className="mt-0.5 text-sm text-gray-800 dark:text-white/90">{value}</div>
  </div>
);

interface CallDetailModalProps {
  call: CallEntry | null;
  onClose: () => void;
}

export const CallDetailModal: React.FC<CallDetailModalProps> = ({ call, onClose }) => {
  if (!call) return null;

  const dtmf = call.dtmfEvents ?? [];
  const collected = call.collectedData ?? [];

  return (
    <Modal isOpen onClose={onClose} className="max-w-2xl p-6">
      <div className="flex flex-col gap-5">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
              {call.phone}
            </h3>
            <CallStatusBadge status={call.status} />
          </div>
          {call.customerName && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {call.customerName}
              {call.customerDocument ? ` · ${call.customerDocument}` : ""}
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <Field
            label="AMD"
            value={call.amdStatus ? (AMD_LABELS[call.amdStatus] ?? call.amdStatus) : "—"}
          />
          <Field
            label="Marcación"
            value={
              call.dialStatus
                ? (DIAL_STATUS_LABELS[call.dialStatus] ?? call.dialStatus)
                : "—"
            }
          />
          <Field label="Intento" value={`#${call.attemptNumber}`} />
          <Field label="Transferida" value={call.transferred ? "Sí" : "No"} />
          <Field
            label="Duración"
            value={call.durationSeconds != null ? `${call.durationSeconds}s` : "—"}
          />
          <Field label="Último evento" value={call.lastEvent ?? "—"} />
          <Field label="Inicio" value={formatTime(call.startedAt)} />
          <Field label="Contestó" value={formatTime(call.answeredAt)} />
          <Field label="Fin" value={formatTime(call.endedAt)} />
        </div>

        {(call.ivrEndNodeId || call.ivrEndReason) && (
          <div className="grid grid-cols-2 gap-4">
            <Field label="Nodo final del flujo" value={call.ivrEndNodeId ?? "—"} />
            <Field label="Motivo de cierre" value={call.ivrEndReason ?? "—"} />
          </div>
        )}

        {dtmf.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Teclas marcadas
            </p>
            <ol className="flex flex-col gap-1.5">
              {dtmf.map((event, index) => (
                <li
                  key={`${event.nodeId}-${event.timestamp}-${index}`}
                  className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300"
                >
                  <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-brand-50 text-xs font-semibold text-brand-600 dark:bg-brand-500/15 dark:text-brand-400">
                    {event.digit ?? "?"}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    en <span className="font-medium">{event.nodeId ?? "—"}</span>
                    {event.nextNode ? ` → ${event.nextNode}` : ""}
                  </span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {collected.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Datos capturados
            </p>
            <ul className="flex flex-col gap-1.5">
              {collected.map((item, index) => (
                <li
                  key={`${item.variable}-${item.timestamp}-${index}`}
                  className="text-sm text-gray-700 dark:text-gray-300"
                >
                  <span className="text-gray-500 dark:text-gray-400">
                    {item.variable ?? "variable"}:
                  </span>{" "}
                  <span className="font-medium">{item.collected_data ?? "—"}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Modal>
  );
};
