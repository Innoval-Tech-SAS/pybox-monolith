import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { CHANNEL_CHAR_LIMITS, UNAVAILABLE_CHANNELS } from "@/templates/constants/template-wizard-options";
import type { Template } from "@/types/templates/template-types";
import type { TemplateEditorFormState } from "@/templates/types/template-editor-form-state";

const EMPTY: TemplateEditorFormState = {
  name: "",
  channel: "EMAIL",
  status: "DRAFT",
  body: "",
  design: null,
  subject: "",
  senderName: "",
  senderEmail: "",
  replyTo: "",
};

export const useTemplateEditorForm = (
  orgId: string,
  id: string | undefined,
  onSaved: () => void,
  onLoadError: () => void,
) => {
  const { apiClient } = useApiClient();
  const isEditing = !!id;

  const [form, setForm] = useState<TemplateEditorFormState>(EMPTY);
  const [loadingTemplate, setLoadingTemplate] = useState(isEditing);
  const [saving, setSaving] = useState(false);

  // En modo edición, cargar la plantilla existente
  useEffect(() => {
    if (!isEditing || !orgId) return;
    apiClient(`/templates/${id}?organizationId=${orgId}`, { method: "GET" })
      .then((t: Template) => {
        setForm({
          name: t.name,
          channel: t.channel,
          status: t.status,
          body: t.body,
          design: t.design ?? null,
          subject: t.subject ?? "",
          senderName: t.senderName ?? "",
          senderEmail: t.senderEmail ?? "",
          replyTo: t.replyTo ?? "",
        });
      })
      .catch(onLoadError)
      .finally(() => setLoadingTemplate(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const set = <K extends keyof TemplateEditorFormState>(key: K) =>
    (value: TemplateEditorFormState[K]) =>
      setForm((prev) => ({ ...prev, [key]: value }));

  const isEmail = form.channel === "EMAIL";
  const isUnavailable = UNAVAILABLE_CHANNELS.includes(form.channel);
  const charLimit = CHANNEL_CHAR_LIMITS[form.channel];
  const withinCharLimit = charLimit === undefined || form.body.length <= charLimit;

  const isDesignValid = !isUnavailable && form.body.trim() !== "" && withinCharLimit;

  const canAdvance = (step: number) => {
    if (step === 0) return true;
    if (step === 1) {
      if (!form.name.trim()) return false;
      if (isEmail) return !!form.subject.trim() && !!form.senderEmail.trim();
      return true;
    }
    if (step === 2) return isDesignValid;
    return false;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      channel: form.channel,
      status: form.status,
      body: form.body,
      design: isEmail ? form.design : null,
      subject: isEmail ? form.subject.trim() || null : null,
      senderName: form.senderName.trim() || null,
      senderEmail: isEmail ? form.senderEmail.trim() || null : null,
      replyTo: isEmail ? form.replyTo.trim() || null : null,
    };
    try {
      if (isEditing) {
        await apiClient(`/templates/${id}?organizationId=${orgId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/templates/?organizationId=${orgId}`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      onSaved();
    } finally {
      setSaving(false);
    }
  };

  return {
    form,
    set,
    isEditing,
    loadingTemplate,
    saving,
    isEmail,
    isUnavailable,
    charLimit,
    isDesignValid,
    canAdvance,
    handleSubmit,
  };
};
