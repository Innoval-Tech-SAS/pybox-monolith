import type { EntityFormState } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";
import type { AggregationStepPatch } from "@/ui/types/step-aggregation-props";

export interface StepAggregationProps {
  state: EntityFormState;
  update: (patch: AggregationStepPatch) => void;
  config: QueryBuilderEntityConfig;
}
