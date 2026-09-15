import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export const SEGMENT_QUERY_BUILDER_CONFIG: QueryBuilderEntityConfig = {
  kind: "segments",
  configKey: "filterCriteria",
  mainTables: [
    { name: "deudores", label: "Deudores" },
    { name: "creditos", label: "Créditos" },
  ],
  additionalTables: [
    { name: "creditos", label: "Créditos" },
    { name: "pagos", label: "Pagos" },
    { name: "metodos_pago", label: "Métodos de pago" },
    { name: "metodos_contacto", label: "Métodos de contacto" },
    { name: "direcciones", label: "Direcciones" },
    { name: "deudores", label: "Deudores" },
  ],
  allTables: [
    { name: "deudores", label: "Deudores" },
    { name: "creditos", label: "Créditos" },
    { name: "pagos", label: "Pagos" },
    { name: "metodos_pago", label: "Métodos de pago" },
    { name: "metodos_contacto", label: "Métodos de contacto" },
    { name: "direcciones", label: "Direcciones" },
  ],
  steps: [
    "Información básica",
    "Tablas y filtros",
    "Uniones",
    "Agregación",
    "Resumen",
  ],
  copy: {
    entityNoun: "segmento",
    entityNounPlural: "segmentos",
    toggleHelpExample: "deudores con más de un crédito vencido",
    havingExampleMetric: "count_creditos",
    namePlaceholder: "Ej. Deudores con créditos vencidos",
    descriptionPlaceholder: "Descripción opcional del segmento",
  },
};
