import type { EntityResponse } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface EntityFormProps {
  config: QueryBuilderEntityConfig;
  scopeId: string;
  onSuccess: () => void;
  onCancel: () => void;
  existing?: EntityResponse;
}
