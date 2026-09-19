import type { Template } from "@/types/templates/template-types";

export type WhatsAppTemplateCategory = "UTILITY" | "MARKETING" | "AUTHENTICATION";

// Meta exige `param_name` en snake_case tal cual, por eso estas claves no se camelizan.
export interface WhatsAppNamedParamExample {
  param_name: string;
  example: string;
}

export interface WhatsAppHeaderComponent {
  type: "HEADER";
  format: "TEXT";
  text: string;
}

export interface WhatsAppBodyComponent {
  type: "BODY";
  text: string;
  example?: { body_text_named_params: WhatsAppNamedParamExample[] };
}

export interface WhatsAppFooterComponent {
  type: "FOOTER";
  text: string;
}

export type WhatsAppTemplateComponent =
  | WhatsAppHeaderComponent
  | WhatsAppBodyComponent
  | WhatsAppFooterComponent;

export interface WhatsAppTemplateCreatePayload {
  name: string;
  language: string;
  category: WhatsAppTemplateCategory;
  components: WhatsAppTemplateComponent[];
}

export interface WhatsAppTemplateData {
  templateId: string;
  metaTemplateId?: string | null;
  metaName: string;
  language: string;
  category: WhatsAppTemplateCategory;
  metaStatus: string;
}

export interface WhatsAppTemplateResponse {
  template: Template;
  whatsapp: WhatsAppTemplateData;
}

export interface WhatsAppTemplateListResponse {
  items: WhatsAppTemplateResponse[];
  total: number;
  page: number;
  pageSize: number;
}
