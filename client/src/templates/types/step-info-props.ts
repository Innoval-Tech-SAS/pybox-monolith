import type { TemplateEditorFormState } from "@/templates/types/template-editor-form-state";

export interface StepInfoProps {
  form: TemplateEditorFormState;
  isEmail: boolean;
  set: <K extends keyof TemplateEditorFormState>(
    key: K,
  ) => (value: TemplateEditorFormState[K]) => void;
}
