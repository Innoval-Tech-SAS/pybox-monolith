import type { EntityResponse } from "@/query-builder/types/query-builder-types";
import type { IvrFlowSummary } from "@/ivr/types/ivr-flow-record";
import type { CampaignEditorFormState } from "./campaign-editor-form-state";

export interface StepIvrFlowProps {
  form: CampaignEditorFormState;
  segments: EntityResponse[];
  flows: IvrFlowSummary[];
  loadingFlows: boolean;
  /** Enlace al diseñador IVR (opcionalmente para editar un flujo existente). */
  designerHref: (flowId?: string) => string;
  set: <K extends keyof CampaignEditorFormState>(key: K) => (value: CampaignEditorFormState[K]) => void;
}
