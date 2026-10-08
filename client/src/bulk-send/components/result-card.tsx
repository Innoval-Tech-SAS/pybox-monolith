import { CheckCircle, Send, SkipForward, Users, XCircle } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { StatItem } from "@/bulk-send/components/stat-item";
import type { ResultCardProps } from "@/bulk-send/types/result-card-props";

export const ResultCard: React.FC<ResultCardProps> = ({ result, onReset }) => (
  <div className="mx-auto flex max-w-2xl flex-col gap-5">
    <Card>
      <CardTitle>Resultado del envío</CardTitle>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mt-1">
        <StatItem icon={<Send size={18} className="text-brand-500" />} label="Procesados" value={result.total_sent} />
        <StatItem icon={<CheckCircle size={18} className="text-success-500" />} label="Exitosos" value={result.success_count} />
        <StatItem icon={<XCircle size={18} className="text-error-500" />} label="Fallidos" value={result.failure_count} />
        <StatItem icon={<Users size={18} className="text-blue-500" />} label="Únicos" value={result.unique_customers} />
      </div>
      {result.skipped_rows > 0 && (
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-warning-50 px-4 py-3 text-sm text-warning-700 dark:bg-warning-900/20 dark:text-warning-400">
          <SkipForward size={16} />
          <span>{result.skipped_rows} {result.skipped_rows === 1 ? "fila omitida" : "filas omitidas"} por datos inválidos o destinatario duplicado.</span>
        </div>
      )}
    </Card>
    <div className="flex justify-end">
      <button
        type="button"
        onClick={onReset}
        className="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
      >
        Nuevo envío
      </button>
    </div>
  </div>
);
