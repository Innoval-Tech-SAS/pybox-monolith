import { Mail, MessageSquare, MessageCircle, Phone, Bot } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import type { StepChannelProps } from "@/campaigns/types/step-channel-props";
import type { ChannelName } from "@/types/channels/channel-types";

const ICONS: Record<ChannelName, React.ReactNode> = {
  SMS: <MessageSquare size={18} />,
  EMAIL: <Mail size={18} />,
  WHATSAPP: <MessageCircle size={18} />,
  CALL: <Phone size={18} />,
  CALL_IA: <Bot size={18} />,
};

export const StepChannel: React.FC<StepChannelProps> = ({ channels, value, onChange }) => (
  <Card className="h-full overflow-y-auto custom-scrollbar">
    <CardTitle>Canal de envío</CardTitle>
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {channels.map((channel) => {
        const isSelected = channel.id === value;
        return (
          <button
            key={channel.id}
            type="button"
            onClick={() => onChange(channel.id)}
            className={`flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition ${
              isSelected
                ? "border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-500/10"
                : "border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-white/3"
            }`}
          >
            <span className={isSelected ? "text-brand-600 dark:text-brand-400" : "text-gray-500 dark:text-gray-400"}>
              {ICONS[channel.name]}
            </span>
            <span className="text-sm font-semibold text-gray-800 dark:text-white/90">{channel.label}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{channel.description}</span>
          </button>
        );
      })}
    </div>
  </Card>
);
