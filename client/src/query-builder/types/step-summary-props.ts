import type { EntityFormState } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface StepSummaryProps {
  state: EntityFormState;
  config: QueryBuilderEntityConfig;
}

export interface SectionProps {
  title: string;
  children: React.ReactNode;
}

export interface RowProps {
  label: string;
  value: string;
}
