import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { SEGMENT_STEPS } from "@/segments/constants/segment.constants";
import type {
  SegmentFormState,
  SegmentFormTable,
  SegmentJoin,
  SegmentTableFilter,
  SegmentGroupBy,
  SegmentAggregation,
  SegmentHaving,
  SegmentOrderBy,
  SegmentResponse,
} from "@/segments/types/segment.types";

const EMPTY_STATE: SegmentFormState = {
  name: "",
  description: "",
  mainTable: "",
  mainTableColumns: [],
  mainTableFilters: [],
  additionalTables: [],
  joins: [],
  aggregateMode: false,
  groupBy: [],
  aggregations: [],
  having: [],
  orderBy: [],
};

const parseExisting = (segment: SegmentResponse): SegmentFormState => {
  const criteria = segment.filterCriteria as Record<string, unknown>;
  const tables = (criteria.tables ?? []) as Record<string, unknown>[];
  const joins = (criteria.joins ?? []) as Record<string, unknown>[];

  const main = tables[0] ?? {};
  const rest = tables.slice(1);

  return {
    name: segment.name,
    description: segment.description ?? "",
    mainTable: (main.name as string) ?? "",
    mainTableColumns: (main.columns as string[]) ?? [],
    mainTableFilters: ((main.filters as Record<string, unknown>[]) ?? []).map((f) => ({
      column: f.column as string,
      op: f.op as SegmentTableFilter["op"],
      value: (f.value as string | string[] | null) ?? null,
    })),
    additionalTables: rest.map((t) => ({
      name: t.name as string,
      alias: (t.alias as string) ?? (t.name as string),
      columns: (t.columns as string[]) ?? [],
      filters: ((t.filters as Record<string, unknown>[]) ?? []).map((f) => ({
        column: f.column as string,
        op: f.op as SegmentTableFilter["op"],
        value: (f.value as string | string[] | null) ?? null,
      })),
    })),
    joins: joins.map((j) => ({
      left: j.left as string,
      right: j.right as string,
      leftOn: ((j.left_on ?? j.leftOn) as string) ?? "",
      rightOn: ((j.right_on ?? j.rightOn) as string) ?? "",
      how: (j.how as SegmentJoin["how"]) ?? "inner",
    })),
    aggregateMode: (criteria.query_mode as string) === "aggregate",
    groupBy: ((criteria.group_by as Record<string, unknown>[]) ?? []).map((g) => ({
      table: (g.table as string) ?? "",
      column: g.column as string,
      alias: (g.alias as string) ?? (g.column as string),
    })),
    aggregations: ((criteria.aggregations as Record<string, unknown>[]) ?? []).map((a) => ({
      function: a.function as SegmentAggregation["function"],
      table: (a.table as string) ?? "",
      column: a.column as string,
      alias: (a.alias as string) ?? "",
    })),
    having: ((criteria.having as Record<string, unknown>[]) ?? []).map((h) => ({
      metric: h.metric as string,
      op: h.op as SegmentHaving["op"],
      value: (h.value as string | string[] | null) ?? null,
    })),
    orderBy: ((criteria.order_by as Record<string, unknown>[]) ?? []).map((o) => ({
      field: o.field as string,
      direction: ((o.direction as string) ?? "asc") as SegmentOrderBy["direction"],
    })),
  };
};

const buildPayload = (state: SegmentFormState, orgId: string) => {
  const tables = [
    {
      name: state.mainTable,
      alias: state.mainTable,
      columns: state.mainTableColumns,
      filters: state.mainTableFilters,
    },
    ...state.additionalTables.map((t) => ({
      name: t.name,
      alias: t.alias,
      columns: t.columns,
      filters: t.filters,
    })),
  ];

  return {
    name: state.name,
    description: state.description || undefined,
    filterCriteria: {
      tables,
      joins: state.joins.map((j) => ({
        left: j.left,
        right: j.right,
        leftOn: j.leftOn,
        rightOn: j.rightOn,
        how: j.how,
      })),
      queryMode: state.aggregateMode ? "aggregate" : "detail",
      groupBy: state.aggregateMode ? state.groupBy : [],
      aggregations: state.aggregateMode ? state.aggregations : [],
      having: state.aggregateMode ? state.having : [],
      orderBy: state.aggregateMode ? state.orderBy : [],
    },
    organizationId: orgId,
  };
};

export const useSegmentForm = (
  orgId: string,
  onSuccess: () => void,
  existing?: SegmentResponse,
) => {
  const { apiClient } = useApiClient();
  const [step, setStep] = useState(0);
  const [state, setState] = useState<SegmentFormState>(
    existing ? parseExisting(existing) : EMPTY_STATE,
  );
  const [submitting, setSubmitting] = useState(false);

  const update = (patch: Partial<SegmentFormState>) =>
    setState((prev) => ({ ...prev, ...patch }));

  const nextStep = () => setStep((s) => Math.min(s + 1, SEGMENT_STEPS.length - 1));
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  // Additional tables helpers
  const addTable = (table: SegmentFormTable) =>
    update({ additionalTables: [...state.additionalTables, table] });

  const removeTable = (alias: string) =>
    update({
      additionalTables: state.additionalTables.filter((t) => t.alias !== alias),
      joins: state.joins.filter((j) => j.left !== alias && j.right !== alias),
    });

  const updateTable = (alias: string, patch: Partial<SegmentFormTable>) =>
    update({
      additionalTables: state.additionalTables.map((t) =>
        t.alias === alias ? { ...t, ...patch } : t,
      ),
    });

  // Joins helpers
  const addJoin = (join: SegmentJoin) =>
    update({ joins: [...state.joins, join] });

  const removeJoin = (index: number) =>
    update({ joins: state.joins.filter((_, i) => i !== index) });

  const updateJoin = (index: number, patch: Partial<SegmentJoin>) =>
    update({
      joins: state.joins.map((j, i) => (i === index ? { ...j, ...patch } : j)),
    });

  const submit = async () => {
    setSubmitting(true);
    try {
      const payload = buildPayload(state, orgId);
      if (existing) {
        await apiClient(`/segments/${existing.id}?organizationId=${orgId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/segments/?organizationId=${orgId}`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      onSuccess();
    } catch {
      // apiClient already shows toast on error
    } finally {
      setSubmitting(false);
    }
  };

  const allTableAliases = [
    { alias: state.mainTable, label: state.mainTable },
    ...state.additionalTables.map((t) => ({ alias: t.alias, label: `${t.name} (${t.alias})` })),
  ];

  return {
    step,
    state,
    update,
    submitting,
    nextStep,
    prevStep,
    addTable,
    removeTable,
    updateTable,
    addJoin,
    removeJoin,
    updateJoin,
    submit,
    allTableAliases,
  };
};
