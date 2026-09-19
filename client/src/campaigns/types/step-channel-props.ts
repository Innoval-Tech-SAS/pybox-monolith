import type { Channel } from "@/types/channels/channel-types";

export interface StepChannelProps {
  channels: Channel[];
  value: string;
  onChange: (channelId: string) => void;
}
