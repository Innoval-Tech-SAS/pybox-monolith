import type { EntityResponse } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface EntityExecutionsHistoryProps {
  config: QueryBuilderEntityConfig;
  isOpen: boolean;
  onClose: () => void;
  entity: EntityResponse;
  scopeId: string;
}
