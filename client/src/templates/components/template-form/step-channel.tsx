import { Card, CardTitle } from "@/ui/components/card";
import { ChannelPicker } from "@/templates/components/channel-picker";
import type { StepChannelProps } from "@/templates/types/step-channel-props";

export const StepChannel: React.FC<StepChannelProps> = ({ channel, disabled, onChange }) => (
  <Card className="flex h-full flex-col">
    <CardTitle>Canal de la plantilla</CardTitle>
    <ChannelPicker value={channel} disabled={disabled} onChange={onChange} />
  </Card>
);
