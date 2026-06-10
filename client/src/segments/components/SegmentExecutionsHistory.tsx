import { useEffect } from "react";
import { FileDown } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Modal } from "@/ui/components/modal/modal";
import { useSegmentExecutions } from "@/segments/hooks/use-segment-execute";
import type { SegmentResponse } from "@/segments/types/segment.types";

interface SegmentExecutionsHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  segment: SegmentResponse;
  orgId: string;
}

export const SegmentExecutionsHistory: React.FC<SegmentExecutionsHistoryProps> = ({
  isOpen,
  onClose,
  segment,
  orgId,
}) => {
  const { executions, loading, fetchExecutions } = useSegmentExecutions(orgId, segment.id);

  useEffect(() => {
    if (isOpen) fetchExecutions();
  }, [isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-2xl mx-4 p-6">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white">
        Historial — {segment.name}
      </h2>

      {loading ? (
        <div className="py-12">
          <Loader />
        </div>
      ) : executions.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-12 text-center">
          <span className="text-3xl">📂</span>
          <p className="text-sm text-gray-500 dark:text-gray-400">Sin ejecuciones registradas.</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
          {executions.map((ex) => (
            <div
              key={ex.id}
              className="flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/3"
            >
              <div className="flex items-center gap-3">
                <Badge
                  variant="light"
                  color={ex.mode === "audit" ? "success" : "primary"}
                  size="sm"
                >
                  {ex.mode}
                </Badge>
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    {ex.rows} filas · {ex.columns.length} columnas
                  </p>
                  {ex.fileName && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1 mt-0.5">
                      <FileDown size={12} />
                      {ex.fileName}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
};
