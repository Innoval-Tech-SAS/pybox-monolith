import type { EntityFormState } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface StepBasicInfoProps {
  state: EntityFormState;
  update: (patch: Partial<EntityFormState>) => void;
  config: QueryBuilderEntityConfig;
}
