import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { REPORT_STEPS } from "@/reports/constants/report.constants";
import type {
  ReportFormState,
  ReportFormTable,
  ReportJoin,
  ReportTableFilter,
  ReportGroupBy,
  ReportAggregation,
  ReportHaving,
  ReportOrderBy,
  ReportResponse,
} from "@/reports/types/report.types";

const EMPTY_STATE: ReportFormState = {
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

const parseExisting = (report: ReportResponse): ReportFormState => {
  const config = report.reportConfig as Record<string, unknown>;
  const tables = (config.tables ?? []) as Record<string, unknown>[];
  const joins = (config.joins ?? []) as Record<string, unknown>[];

  const main = tables[0] ?? {};
  const rest = tables.slice(1);

  return {
    name: report.name,
    description: report.description ?? "",
    mainTable: (main.name as string) ?? "",
    mainTableColumns: (main.columns as string[]) ?? [],
    mainTableFilters: ((main.filters as Record<string, unknown>[]) ?? []).map((f) => ({
      column: f.column as string,
      op: f.op as ReportTableFilter["op"],
      value: (f.value as string | string[] | null) ?? null,
    })),
    additionalTables: rest.map((t) => ({
      name: t.name as string,
      alias: (t.alias as string) ?? (t.name as string),
      columns: (t.columns as string[]) ?? [],
      filters: ((t.filters as Record<string, unknown>[]) ?? []).map((f) => ({
        column: f.column as string,
        op: f.op as ReportTableFilter["op"],
        value: (f.value as string | string[] | null) ?? null,
      })),
    })),
    joins: joins.map((j) => ({
      left: j.left as string,
      right: j.right as string,
      leftOn: ((j.left_on ?? j.leftOn) as string) ?? "",
      rightOn: ((j.right_on ?? j.rightOn) as string) ?? "",
      how: (j.how as ReportJoin["how"]) ?? "inner",
    })),
    aggregateMode: (config.query_mode as string) === "aggregate",
    groupBy: ((config.group_by as Record<string, unknown>[]) ?? []).map((g) => ({
      table: (g.table as string) ?? "",
      column: g.column as string,
      alias: (g.alias as string) ?? (g.column as string),
    })),
    aggregations: ((config.aggregations as Record<string, unknown>[]) ?? []).map((a) => ({
      function: a.function as ReportAggregation["function"],
      table: (a.table as string) ?? "",
      column: a.column as string,
      alias: (a.alias as string) ?? "",
    })),
    having: ((config.having as Record<string, unknown>[]) ?? []).map((h) => ({
      metric: h.metric as string,
      op: h.op as ReportHaving["op"],
      value: (h.value as string | string[] | null) ?? null,
    })),
    orderBy: ((config.order_by as Record<string, unknown>[]) ?? []).map((o) => ({
      field: o.field as string,
      direction: ((o.direction as string) ?? "asc") as ReportOrderBy["direction"],
    })),
  };
};

const buildPayload = (state: ReportFormState, orgId: string) => {
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
    reportConfig: {
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

export const useReportForm = (
  orgId: string,
  onSuccess: () => void,
  existing?: ReportResponse,
) => {
  const { apiClient } = useApiClient();
  const [step, setStep] = useState(0);
  const [state, setState] = useState<ReportFormState>(
    existing ? parseExisting(existing) : EMPTY_STATE,
  );
  const [submitting, setSubmitting] = useState(false);

  const update = (patch: Partial<ReportFormState>) =>
    setState((prev) => ({ ...prev, ...patch }));

  const nextStep = () => setStep((s) => Math.min(s + 1, REPORT_STEPS.length - 1));
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  // Additional tables helpers
  const addTable = (table: ReportFormTable) =>
    update({ additionalTables: [...state.additionalTables, table] });

  const removeTable = (alias: string) =>
    update({
      additionalTables: state.additionalTables.filter((t) => t.alias !== alias),
      joins: state.joins.filter((j) => j.left !== alias && j.right !== alias),
    });

  const updateTable = (alias: string, patch: Partial<ReportFormTable>) =>
    update({
      additionalTables: state.additionalTables.map((t) =>
        t.alias === alias ? { ...t, ...patch } : t,
      ),
    });

  // Joins helpers
  const addJoin = (join: ReportJoin) =>
    update({ joins: [...state.joins, join] });

  const removeJoin = (index: number) =>
    update({ joins: state.joins.filter((_, i) => i !== index) });

  const updateJoin = (index: number, patch: Partial<ReportJoin>) =>
    update({
      joins: state.joins.map((j, i) => (i === index ? { ...j, ...patch } : j)),
    });

  const submit = async () => {
    setSubmitting(true);
    try {
      const payload = buildPayload(state, orgId);
      if (existing) {
        await apiClient(`/reports/${existing.id}?organizationId=${orgId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/reports/?organizationId=${orgId}`, {
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
