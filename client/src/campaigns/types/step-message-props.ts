import type { SegmentResponse } from "@/segments/types/segment.types";
import type { Template } from "@/types/templates/template-types";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { CampaignEditorFormState } from "./campaign-editor-form-state";

export interface StepMessageProps {
  form: CampaignEditorFormState;
  segments: SegmentResponse[];
  compatibleTemplates: Template[];
  selectedTemplate: Template | null;
  showsSubject: boolean;
  variables: TemplateVariableOption[];
  set: <K extends keyof CampaignEditorFormState>(key: K) => (value: CampaignEditorFormState[K]) => void;
}
