import type { EntityExecuteResponse } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface EntityResultsTableProps {
  config: QueryBuilderEntityConfig;
  result: EntityExecuteResponse;
}
