import type { EntityResponse } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface EntityTableProps {
  config: QueryBuilderEntityConfig;
  entities: EntityResponse[];
  loading: boolean;
  total: number;
  page: number;
  pages: number;
  onEdit: (entity: EntityResponse) => void;
  onExecute: (entity: EntityResponse) => void;
  onHistory: (entity: EntityResponse) => void;
  onDelete: (entity: EntityResponse) => void;
  onPageChange: (page: number) => void;
}

export interface ActionBtnProps {
  title: string;
  onClick: () => void;
  icon: React.ReactNode;
  danger?: boolean;
}
