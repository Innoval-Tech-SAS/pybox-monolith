import { PhoneCall } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Loader } from "@/ui/components/loader/loader";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import { CallStatusBadge } from "./call-status-badge";
import { AMD_LABELS } from "../constants/call-status-labels";
import { isTerminalCall } from "../types/ivr-monitor-types";
import type { CallEntry } from "../hooks/use-call-monitor";

/** Tope de filas renderizadas: una campaña masiva puede tener cientos en vuelo. */
const MAX_ROWS = 100;

const formatDuration = (seconds: number): string => {
  const safe = Math.max(0, Math.floor(seconds));
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
};

/**
 * Duración a mostrar. Para una llamada terminada manda el dato del backend;
 * para una en curso se calcula contra el reloj local, porque el backend solo
 * conoce la duración cuando la llamada cierra.
 */
const resolveDuration = (call: CallEntry): string => {
  if (isTerminalCall(call.status)) {
    return call.durationSeconds != null ? formatDuration(call.durationSeconds) : "—";
  }
  const start = call.answeredAt ?? call.startedAt;
  if (!start) return "—";
  const elapsed = (Date.now() - new Date(start).getTime()) / 1000;
  return elapsed >= 0 ? formatDuration(elapsed) : "—";
};

interface ActiveCallsTableProps {
  calls: CallEntry[];
  loading: boolean;
  /** Cambia cada segundo; fuerza el repintado de los cronómetros. */
  tick: number;
  onSelect: (call: CallEntry) => void;
}

export const ActiveCallsTable: React.FC<ActiveCallsTableProps> = ({
  calls,
  loading,
  onSelect,
}) => {
  const visible = calls.slice(0, MAX_ROWS);
  const hidden = calls.length - visible.length;

  return (
    <div className="flex flex-1 min-h-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/5 dark:bg-white/3">
      <div className="flex-1 min-h-0 overflow-auto custom-scrollbar">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 dark:border-gray-800">
              {["Teléfono", "Cliente", "Estado", "AMD", "Tecla", "Intento", "Duración"].map(
                (label) => (
                  <TableCell
                    key={label}
                    isHeader
                    className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
                  >
                    {label}
                  </TableCell>
                ),
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell className="px-4 py-10 text-center" colSpan={7}>
                  <Loader size="sm" loaderText="Cargando llamadas..." />
                </TableCell>
              </TableRow>
            ) : visible.length === 0 ? (
              <TableRow>
                <TableCell className="px-4 py-10 text-center" colSpan={7}>
                  <EmptyState
                    icon={PhoneCall}
                    title="Sin llamadas en curso. Aparecerán aquí en cuanto la campaña empiece a marcar."
                  />
                </TableCell>
              </TableRow>
            ) : (
              visible.map((call) => (
                <TableRow
                  key={call.interactionId}
                  onClick={() => onSelect(call)}
                  className={`cursor-pointer border-b border-gray-100 last:border-0 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/3 ${
                    call.terminalAt !== null ? "opacity-60" : ""
                  }`}
                >
                  <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                    {call.phone}
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {call.customerName || "—"}
                    </p>
                    {call.customerDocument && (
                      <p className="text-xs text-gray-400 dark:text-gray-500">
                        {call.customerDocument}
                      </p>
                    )}
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    <CallStatusBadge status={call.status} />
                  </TableCell>
                  <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {call.amdStatus ? (AMD_LABELS[call.amdStatus] ?? call.amdStatus) : "—"}
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    {call.lastDigit ? (
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-md bg-brand-50 text-xs font-semibold text-brand-600 dark:bg-brand-500/15 dark:text-brand-400">
                        {call.lastDigit}
                      </span>
                    ) : (
                      <span className="text-sm text-gray-400">—</span>
                    )}
                  </TableCell>
                  <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {call.attemptNumber > 1 ? `#${call.attemptNumber}` : "—"}
                  </TableCell>
                  <TableCell className="px-4 py-3 font-mono text-sm tabular-nums text-gray-600 dark:text-gray-400">
                    {resolveDuration(call)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {hidden > 0 && (
        <div className="shrink-0 border-t border-gray-100 px-4 py-2 text-center text-xs text-gray-500 dark:border-white/5 dark:text-gray-400">
          y {hidden} llamada{hidden === 1 ? "" : "s"} más en curso
        </div>
      )}
    </div>
  );
};
