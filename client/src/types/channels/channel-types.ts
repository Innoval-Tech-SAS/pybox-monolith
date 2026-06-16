export type ChannelName = "SMS" | "EMAIL" | "WHATSAPP" | "CALL";
export type Currency = "USD" | "EUR" | "COP" | "MXN";

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
