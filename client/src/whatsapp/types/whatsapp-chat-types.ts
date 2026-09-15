export type WhatsAppMessageDirection = "ENTRANTE" | "SALIENTE";

export interface WhatsAppChat {
  id: string;
  organizationId: string;
  organizationName: string;
  phone: string;
  profileName: string | null;
  debtorId: string | null;
  portfolioId: string | null;
  campaignId: string | null;
  assignedUserId: string | null;
  lastMessageAt: string | null;
  createdAt: string;
}

export interface WhatsAppChatsPage {
  items: WhatsAppChat[];
  total: number;
  page: number;
  pageSize: number;
}

export interface WhatsAppMessage {
  id: string;
  chatId: string;
  direction: WhatsAppMessageDirection;
  wamid: string | null;
  messageType: string;
  content: string | null;
  sentAt: string;
}

export interface WhatsAppChatDebtor {
  id: string;
  fullName: string;
  debtorType: string;
  documentType: string;
  documentNumber: string;
}

export interface WhatsAppChatPortfolioInfo {
  id: string;
  name: string;
}

export interface WhatsAppChatCampaignInfo {
  id: string;
  name: string;
  status: string;
}

export interface WhatsAppChatCredit {
  id: string;
  creditNumber: string;
  creditType: string;
  disbursedDate: string;
  totalCreditBalance: number;
  overduePrincipalBalance: number;
  daysOverdueAtCutoff: number;
  overdueInstallments: number;
  pendingInstallments: number;
  currencyCode: string;
}

export interface WhatsAppChatDetails {
  debtor: WhatsAppChatDebtor | null;
  isSelfRegistered: boolean;
  portfolio: WhatsAppChatPortfolioInfo | null;
  campaign: WhatsAppChatCampaignInfo | null;
  credits: WhatsAppChatCredit[];
}

export type WsWhatsAppEvent =
  | { event: "chats"; data: WhatsAppChatsPage }
  | { event: "messages"; data: WhatsAppMessage[] }
  | { event: "message"; data: WhatsAppMessage }
  | { event: "new_message"; data: WhatsAppMessage }
  | { event: "error"; data: { detail: string } };
