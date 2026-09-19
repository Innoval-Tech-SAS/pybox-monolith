import { Mail, MessageSquare, MessageCircle, Phone, Bot } from "lucide-react";
import type { ChannelIconName } from "@/templates/constants/template-wizard-options";

export const CHANNEL_PICKER_ICONS: Record<ChannelIconName, React.ReactNode> = {
  mail: <Mail size={18} />,
  sms: <MessageSquare size={18} />,
  whatsapp: <MessageCircle size={18} />,
  call: <Phone size={18} />,
  "call-ia": <Bot size={18} />,
};
