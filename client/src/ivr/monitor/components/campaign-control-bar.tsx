import { useState } from "react";
import { Pause, Play, Square } from "lucide-react";
import { Button } from "@/ui/components/button/button";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import type { IvrExecution } from "../types/ivr-execution-types";
import { TERMINAL_EXECUTION_STATUSES } from "../types/ivr-execution-types";

const STATUS_LABELS: Record<string, string> = {
  PENDING: "Pendiente",
  RUNNING: "En marcha",
  PAUSED: "Pausada",
  CANCELLED: "Cancelada",
  FINISHED: "Finalizada",
};

const STATUS_CLASSES: Record<string, string> = {
  PENDING: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  RUNNING: "bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400",
  PAUSED: "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-warning-400",
  CANCELLED: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  FINISHED: "bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-400",
};

interface CampaignControlBarProps {
  execution: IvrExecution | null;
  loading: boolean;
  acting: boolean;
  onPause: () => void;
  onResume: () => void;
  onCancel: () => void;
}

/**
 * Controles del bulk activo de la campaña. Si hay más de un bulk (envíos
 * grandes troceados, o una campaña recurrente con varios disparos) opera
 * sobre el más reciente — `useIvrExecution` ya lo resuelve así.
 */
export const CampaignControlBar: React.FC<CampaignControlBarProps> = ({
  execution,
  loading,
  acting,
  onPause,
  onResume,
  onCancel,
}) => {
  const [confirmingCancel, setConfirmingCancel] = useState(false);

  if (loading) return null;

  if (!execution) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Esta campaña todavía no ha despachado ninguna llamada.
      </p>
    );
  }

  const isTerminal = TERMINAL_EXECUTION_STATUSES.includes(execution.status);

  return (
    <>
      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-white/5 dark:bg-white/3">
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_CLASSES[execution.status]}`}
        >
          {STATUS_LABELS[execution.status]}
        </span>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          bulk {execution.bulkId.slice(0, 8)}… · {execution.quantity} destinatarios
        </span>

        <div className="ml-auto flex items-center gap-2">
          {execution.status === "RUNNING" && (
            <Button size="sm" variant="outline" startIcon={<Pause size={14} />} onClick={onPause} disabled={acting}>
              Pausar
            </Button>
          )}
          {execution.status === "PAUSED" && (
            <Button size="sm" variant="outline" startIcon={<Play size={14} />} onClick={onResume} disabled={acting}>
              Reanudar
            </Button>
          )}
          {!isTerminal && (
            <Button
              size="sm"
              variant="outline"
              startIcon={<Square size={14} />}
              onClick={() => setConfirmingCancel(true)}
              disabled={acting}
              className="border-error-300 text-error-600 hover:bg-error-50 dark:border-error-500/30 dark:text-error-400"
            >
              Cancelar
            </Button>
          )}
        </div>
      </div>

      <ConfirmModal
        isOpen={confirmingCancel}
        onClose={() => setConfirmingCancel(false)}
        onConfirm={() => {
          setConfirmingCancel(false);
          onCancel();
        }}
        title="Cancelar la campaña"
        message="Esta acción es irreversible: Helena descartará las llamadas pendientes de este bulk y no se puede reanudar."
        confirmLabel="Sí, cancelar"
        variant="danger"
        loading={acting}
      />
    </>
  );
};
