export type ChannelName = "SMS" | "EMAIL" | "WHATSAPP" | "CALL" | "CALL_IA";
export type Currency = "USD" | "COP" | "MXN" | "ARS" | "PEN" | "VES";

export interface Channel {
  id: string;
  name: ChannelName;
  label: string;
  currency: Currency;
  unitPrice: string;
  description: string;
  createdAt: string;
  updatedAt?: string | null;
}
