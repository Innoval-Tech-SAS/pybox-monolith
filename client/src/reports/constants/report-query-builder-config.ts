import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export const REPORT_QUERY_BUILDER_CONFIG: QueryBuilderEntityConfig = {
  kind: "reports",
  configKey: "reportConfig",
  mainTables: [
    { name: "deudores", label: "Deudores" },
    { name: "metodos_contacto", label: "Métodos de contacto" },
  ],
  additionalTables: [
    { name: "deudores", label: "Deudores" },
    { name: "metodos_contacto", label: "Métodos de contacto" },
    { name: "contactos", label: "Contactos (mensajería)" },
  ],
  allTables: [
    { name: "deudores", label: "Deudores" },
    { name: "metodos_contacto", label: "Métodos de contacto" },
    { name: "contactos", label: "Contactos (mensajería)" },
  ],
  steps: [
    "Información básica",
    "Tablas y filtros",
    "Uniones",
    "Agregación",
    "Resumen",
  ],
  copy: {
    entityNoun: "reporte",
    entityNounPlural: "reportes",
    toggleHelpExample: "deudores con más de un método de contacto",
    havingExampleMetric: "count_metodos_contacto",
    namePlaceholder: "Ej. Deudores con métodos de contacto activos",
    descriptionPlaceholder: "Descripción opcional del reporte",
  },
};
