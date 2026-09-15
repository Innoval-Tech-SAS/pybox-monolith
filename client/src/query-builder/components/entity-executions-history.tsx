import { useEffect } from "react";
import { FileDown, FolderOpen } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Modal } from "@/ui/components/modal/modal";
import { useEntityExecutions } from "@/hooks/use-entity-execution";
import type { EntityExecutionResponse } from "@/query-builder/types/query-builder-types";
import type { EntityExecutionsHistoryProps } from "@/query-builder/types/entity-executions-history-props";

export const EntityExecutionsHistory: React.FC<EntityExecutionsHistoryProps> = ({
  config,
  isOpen,
  onClose,
  entity,
  scopeId,
}) => {
  const { executions, loading, fetchExecutions } = useEntityExecutions<EntityExecutionResponse>(config.kind, scopeId, entity.id);

  useEffect(() => {
    if (isOpen) fetchExecutions();
  }, [isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-2xl mx-4 p-6">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white">
        Historial — {entity.name}
      </h2>

      {loading ? (
        <div className="py-12">
          <Loader />
        </div>
      ) : executions.length === 0 ? (
        <div className="py-12">
          <EmptyState icon={FolderOpen} title="Sin ejecuciones registradas" />
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
