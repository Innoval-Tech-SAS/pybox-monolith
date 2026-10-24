import { describe, expect, it } from "vitest";
import {
  analyzeWhatsAppContent,
  applyNamedExamples,
  buildWhatsAppComponents,
  extractNamedVariables,
  isWhatsAppContentValid,
} from "@/templates/utils/whatsapp-template-components";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";

const VARIABLES: TemplateVariableOption[] = [
  { key: "nombre", label: "Nombre", example: "Juan" },
  { key: "saldo_total", label: "Saldo total", example: "1234.56" },
];

const baseForm = (overrides: Partial<WhatsAppTemplateFormState> = {}): WhatsAppTemplateFormState => ({
  language: "es",
  category: "UTILITY",
  headerText: "",
  bodyText: "Hola {{nombre}}, tu saldo es {{saldo_total}} pesos.",
  footerText: "",
  ...overrides,
});

describe("extractNamedVariables", () => {
  it("devuelve las variables sin repetir y en orden de aparición", () => {
    expect(extractNamedVariables("{{a}} y {{b}} y {{a}}")).toEqual(["a", "b"]);
  });

  it("ignora variables de una sola llave (formato SMS/Email)", () => {
    expect(extractNamedVariables("Hola {nombre}")).toEqual([]);
  });
});

describe("applyNamedExamples", () => {
  it("reemplaza las variables conocidas y deja intactas las desconocidas", () => {
    expect(applyNamedExamples("Hola {{nombre}} {{otra}}", VARIABLES)).toBe("Hola Juan {{otra}}");
  });
});

describe("analyzeWhatsAppContent", () => {
  it("acepta un cuerpo con variables conocidas", () => {
    const issues = analyzeWhatsAppContent(baseForm(), VARIABLES);
    expect(isWhatsAppContentValid(issues)).toBe(true);
    expect(issues.variableAtEdge).toBe(false);
  });

  it("rechaza un cuerpo vacío", () => {
    const issues = analyzeWhatsAppContent(baseForm({ bodyText: "   " }), VARIABLES);
    expect(issues.bodyEmpty).toBe(true);
    expect(isWhatsAppContentValid(issues)).toBe(false);
  });

  it("marca variables sin columna asociada", () => {
    const issues = analyzeWhatsAppContent(baseForm({ bodyText: "Hola {{inexistente}}" }), VARIABLES);
    expect(issues.unknownVariables).toEqual(["inexistente"]);
    expect(isWhatsAppContentValid(issues)).toBe(false);
  });

  it("rechaza variables en encabezado y pie, que el envío no resuelve", () => {
    const issues = analyzeWhatsAppContent(
      baseForm({ headerText: "Hola {{nombre}}", footerText: "{{saldo_total}}" }),
      VARIABLES,
    );
    expect(issues.headerHasVariables).toBe(true);
    expect(issues.footerHasVariables).toBe(true);
    expect(isWhatsAppContentValid(issues)).toBe(false);
  });

  it("respeta los límites de caracteres de Meta", () => {
    const issues = analyzeWhatsAppContent(
      baseForm({ bodyText: "a".repeat(1025), headerText: "b".repeat(61), footerText: "c".repeat(61) }),
      VARIABLES,
    );
    expect(issues.bodyTooLong).toBe(true);
    expect(issues.headerTooLong).toBe(true);
    expect(issues.footerTooLong).toBe(true);
  });

  it("solo advierte (no bloquea) cuando el cuerpo empieza o termina con una variable", () => {
    const issues = analyzeWhatsAppContent(baseForm({ bodyText: "{{nombre}} debe pagar" }), VARIABLES);
    expect(issues.variableAtEdge).toBe(true);
    expect(isWhatsAppContentValid(issues)).toBe(true);
  });
});

describe("buildWhatsAppComponents", () => {
  it("arma solo BODY con ejemplos nombrados cuando no hay encabezado ni pie", () => {
    expect(buildWhatsAppComponents(baseForm(), VARIABLES)).toEqual([
      {
        type: "BODY",
        text: "Hola {{nombre}}, tu saldo es {{saldo_total}} pesos.",
        example: {
          body_text_named_params: [
            { param_name: "nombre", example: "Juan" },
            { param_name: "saldo_total", example: "1234.56" },
          ],
        },
      },
    ]);
  });

  it("incluye HEADER y FOOTER en orden y omite `example` si no hay variables", () => {
    const components = buildWhatsAppComponents(
      baseForm({ headerText: " Aviso ", bodyText: "Pago pendiente.", footerText: " Gracias " }),
      VARIABLES,
    );
    expect(components).toEqual([
      { type: "HEADER", format: "TEXT", text: "Aviso" },
      { type: "BODY", text: "Pago pendiente." },
      { type: "FOOTER", text: "Gracias" },
    ]);
  });
});
