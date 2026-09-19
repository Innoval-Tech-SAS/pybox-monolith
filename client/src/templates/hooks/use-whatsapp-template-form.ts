import { useMemo, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";
import {
  WHATSAPP_DEFAULT_CATEGORY,
  WHATSAPP_DEFAULT_LANGUAGE,
} from "@/templates/constants/whatsapp-template-options";
import {
  analyzeWhatsAppContent,
  buildWhatsAppComponents,
  isWhatsAppContentValid,
} from "@/templates/utils/whatsapp-template-components";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";
import type {
  WhatsAppTemplateCreatePayload,
  WhatsAppTemplateResponse,
} from "@/types/templates/whatsapp-template-types";

const EMPTY: WhatsAppTemplateFormState = {
  language: WHATSAPP_DEFAULT_LANGUAGE,
  category: WHATSAPP_DEFAULT_CATEGORY,
  headerText: "",
  bodyText: "",
  footerText: "",
};

export const useWhatsAppTemplateForm = (
  portfolioId: string,
  variables: TemplateVariableOption[],
) => {
  const { apiClient } = useApiClient();
  const { success } = useToast();

  const [form, setForm] = useState<WhatsAppTemplateFormState>(EMPTY);
  const [saving, setSaving] = useState(false);

  const set = <K extends keyof WhatsAppTemplateFormState>(key: K) =>
    (value: WhatsAppTemplateFormState[K]) =>
      setForm((prev) => ({ ...prev, [key]: value }));

  const issues = useMemo(() => analyzeWhatsAppContent(form, variables), [form, variables]);
  const isDesignValid = isWhatsAppContentValid(issues);

  const canAdvance = (step: number, name: string) => {
    if (step === 0) return true;
    if (step === 1) return !!name.trim() && !!form.language && !!form.category;
    if (step === 2) return isDesignValid;
    return false;
  };

  // Crea la plantilla en Meta vía el flujo propio de WhatsApp: el endpoint genérico
  // /templates/ rechaza `body` para este canal porque el contenido vive en Meta.
  const submit = async (name: string, onSaved: () => void) => {
    setSaving(true);
    const payload: WhatsAppTemplateCreatePayload = {
      name: name.trim(),
      language: form.language,
      category: form.category,
      components: buildWhatsAppComponents(form, variables),
    };
    try {
      await apiClient<WhatsAppTemplateResponse>(`/whatsapp/templates/?portfolioId=${portfolioId}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      success(
        "Plantilla enviada a Meta",
        "Queda pendiente de aprobación. Usa «Refrescar estado» en el listado para ver el resultado.",
      );
      onSaved();
    } finally {
      setSaving(false);
    }
  };

  return { form, set, issues, isDesignValid, canAdvance, saving, submit };
};
