import type { SelectOptionGroup } from "@/types/props/select-props";

export const DOC_TYPE_LABELS: Record<string, string> = {
  CC: "Cédula de Ciudadanía",
  CE: "Cédula de Extranjería",
  NIT: "Número de Identificación Tributaria",
  PEP: "Permiso Especial de Permanencia",
  CURP: "Clave Única de Registro de Población",
  INE: "Instituto Nacional Electoral",
  RFC: "Registro Federal de Contribuyentes",
  DNI: "Documento Nacional de Identidad",
  CUIL: "Código Único de Identificación Laboral",
  CUIT: "Código Único de Identificación Tributaria",
  RUC: "Registro Único de Contribuyentes",
  CI: "Cédula de Identidad",
  RIF: "Registro de Información Fiscal",
  PASAPORTE: "Pasaporte",
};

export const DOCUMENT_TYPE_GROUPS: SelectOptionGroup[] = [
  {
    group: "🇨🇴 Colombia",
    options: [
      { value: "CC",  label: "CC – Cédula de Ciudadanía" },
      { value: "CE",  label: "CE – Cédula de Extranjería" },
      { value: "NIT", label: "NIT – Número de Identificación Tributaria" },
      { value: "PEP", label: "PEP – Permiso Especial de Permanencia" },
    ],
  },
  {
    group: "🇲🇽 México",
    options: [
      { value: "CURP", label: "CURP – Clave Única de Registro de Población" },
      { value: "INE",  label: "INE – Instituto Nacional Electoral" },
      { value: "RFC",  label: "RFC – Registro Federal de Contribuyentes" },
    ],
  },
  {
    group: "🇦🇷 Argentina",
    options: [
      { value: "DNI",  label: "DNI – Documento Nacional de Identidad" },
      { value: "CUIL", label: "CUIL – Código Único de Identificación Laboral" },
      { value: "CUIT", label: "CUIT – Código Único de Identificación Tributaria" },
    ],
  },
  {
    group: "🇵🇪 Perú",
    options: [
      { value: "DNI",      label: "DNI – Documento Nacional de Identidad" },
      { value: "CE",       label: "CE – Cédula de Extranjería" },
      { value: "RUC",      label: "RUC – Registro Único de Contribuyentes" },
    ],
  },
  {
    group: "🇻🇪 Venezuela",
    options: [
      { value: "CI",  label: "CI – Cédula de Identidad" },
      { value: "RIF", label: "RIF – Registro de Información Fiscal" },
    ],
  },
  {
    group: "🌎 Universal",
    options: [
      { value: "PASAPORTE", label: "Pasaporte" },
    ],
  },
];
