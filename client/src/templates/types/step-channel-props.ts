import type { TemplateChannel } from "@/types/templates/template-types";

export interface StepChannelProps {
  channel: TemplateChannel;
  disabled: boolean;
  onChange: (channel: TemplateChannel) => void;
}
