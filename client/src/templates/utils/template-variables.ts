import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

const VARIABLE_PATTERN = /\{(\w+)\}/g;

export function extractVariables(source: string): string[] {
  const matches = [...source.matchAll(VARIABLE_PATTERN)];
  return [...new Set(matches.map((m) => m[1]))];
}

export function applyTemplatePreview(template: string, variables: TemplateVariableOption[]): string {
  let preview = template;
  for (const variable of variables) {
    preview = preview.replace(new RegExp(`\\{${variable.key}\\}`, "g"), variable.example);
  }
  return preview;
}
