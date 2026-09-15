import type { TemplateChannel } from "@/types/templates/template-types";

export interface ChannelPickerProps {
  value: TemplateChannel;
  onChange: (channel: TemplateChannel) => void;
  disabled?: boolean;
}
