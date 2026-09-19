import type { TableOption } from "@/query-builder/types/query-builder-entity-config";

export const getMainTableLabel = (
  criteria: Record<string, unknown>,
  allTables: TableOption[],
): string => {
  const tables = criteria.tables as Array<{ name: string }> | undefined;
  const name = tables?.[0]?.name ?? "";
  return allTables.find((t) => t.name === name)?.label ?? name;
};
