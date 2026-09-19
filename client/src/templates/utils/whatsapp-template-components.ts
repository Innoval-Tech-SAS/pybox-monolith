import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";
import type {
  WhatsAppBodyComponent,
  WhatsAppTemplateComponent,
} from "@/types/templates/whatsapp-template-types";
import {
  WHATSAPP_BODY_MAX_CHARS,
  WHATSAPP_FOOTER_MAX_CHARS,
  WHATSAPP_HEADER_MAX_CHARS,
} from "@/templates/constants/whatsapp-template-options";

// Variables nombradas {{nombre}}, igual que el parser del backend
// (messaging/whatsapp/utils/whatsapp_template_parser.py).
const NAMED_VARIABLE_PATTERN = /\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}/g;
const FALLBACK_EXAMPLE = "Ejemplo";

export interface WhatsAppContentIssues {
  bodyEmpty: boolean;
  bodyTooLong: boolean;
  headerTooLong: boolean;
  footerTooLong: boolean;
  headerHasVariables: boolean;
  footerHasVariables: boolean;
  unknownVariables: string[];
  variableAtEdge: boolean;
}

export function extractNamedVariables(source: string): string[] {
  const matches = [...source.matchAll(NAMED_VARIABLE_PATTERN)];
  return [...new Set(matches.map((m) => m[1]))];
}

export function toVariableToken(key: string): string {
  return `{{${key}}}`;
}

export function applyNamedExamples(text: string, variables: TemplateVariableOption[]): string {
  return text.replace(NAMED_VARIABLE_PATTERN, (token, key: string) => {
    const option = variables.find((v) => v.key === key);
    return option ? option.example : token;
  });
}

function hasVariableAtEdge(text: string): boolean {
  const trimmed = text.trim();
  return /^\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}/.test(trimmed) || /\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}$/.test(trimmed);
}

export function analyzeWhatsAppContent(
  form: WhatsAppTemplateFormState,
  variables: TemplateVariableOption[],
): WhatsAppContentIssues {
  const body = form.bodyText.trim();
  const knownKeys = new Set(variables.map((v) => v.key));
  return {
    bodyEmpty: body === "",
    bodyTooLong: form.bodyText.length > WHATSAPP_BODY_MAX_CHARS,
    headerTooLong: form.headerText.length > WHATSAPP_HEADER_MAX_CHARS,
    footerTooLong: form.footerText.length > WHATSAPP_FOOTER_MAX_CHARS,
    // El envío solo resuelve variables del cuerpo (whatsapp_channel._build_components).
    headerHasVariables: extractNamedVariables(form.headerText).length > 0,
    footerHasVariables: extractNamedVariables(form.footerText).length > 0,
    unknownVariables: extractNamedVariables(body).filter((key) => !knownKeys.has(key)),
    variableAtEdge: hasVariableAtEdge(body),
  };
}

export function isWhatsAppContentValid(issues: WhatsAppContentIssues): boolean {
  return (
    !issues.bodyEmpty &&
    !issues.bodyTooLong &&
    !issues.headerTooLong &&
    !issues.footerTooLong &&
    !issues.headerHasVariables &&
    !issues.footerHasVariables &&
    issues.unknownVariables.length === 0
  );
}

export function buildWhatsAppComponents(
  form: WhatsAppTemplateFormState,
  variables: TemplateVariableOption[],
): WhatsAppTemplateComponent[] {
  const components: WhatsAppTemplateComponent[] = [];

  const header = form.headerText.trim();
  if (header) components.push({ type: "HEADER", format: "TEXT", text: header });

  const body = form.bodyText.trim();
  const bodyComponent: WhatsAppBodyComponent = { type: "BODY", text: body };
  const names = extractNamedVariables(body);
  if (names.length > 0) {
    // Meta exige un ejemplo por cada variable para aprobar la plantilla.
    bodyComponent.example = {
      body_text_named_params: names.map((name) => ({
        param_name: name,
        example: variables.find((v) => v.key === name)?.example || FALLBACK_EXAMPLE,
      })),
    };
  }
  components.push(bodyComponent);

  const footer = form.footerText.trim();
  if (footer) components.push({ type: "FOOTER", text: footer });

  return components;
}
