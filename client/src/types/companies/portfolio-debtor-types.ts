export interface PortfolioDebtor {
  id: string;
  fullName: string;
  documentType: string;
  documentNumber: string;
  debtorType: string;
}

export interface DebtorAddress {
  id: string;
  address: string;
  city: string;
  state: string;
  country: string;
  addressType: string;
}

export interface DebtorContactMethod {
  id: string;
  contactType: string;
  contactValue: string;
}

export interface DebtorDetail {
  id: string;
  fullName: string;
  debtorType: string;
  documentType: string;
  documentNumber: string;
  addresses: DebtorAddress[];
  contactMethods: DebtorContactMethod[];
}

export interface RelatedContactsResponse {
  debtor: DebtorDetail;
  codebtors: DebtorDetail[];
}

export interface DebtorCredit {
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

export interface PortfolioDebtorsResponse {
  items: PortfolioDebtor[];
  total: number;
  page: number;
  pageSize: number;
}

export interface DebtorInstallment {
  id: string;
  installmentNumber: number | null;
  limitPayDate: string;
  paymentDate: string | null;
  paymentAmount: number;
  principalPayment: number;
  currentInterestAmount: number;
  overdueInterestAmount: number;
  totalInterestAmount: number;
  otherCharges: number;
}

export interface DebtorCreditWithInstallments {
  credit: DebtorCredit;
  installments: DebtorInstallment[];
}

export interface DebtorSendingItem {
  id: string;
  content: string;
  recipient: string;
  status: string;
  sentAt: string | null;
  error: string | null;
  createdAt: string;
}

export interface DebtorSendingChannelGroup {
  channelId: string | null;
  channelName: string;
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  items: DebtorSendingItem[];
}

export interface DebtorDocument {
  id: string;
  category: string;
  ownerScope: string;
  originalName: string;
  contentType: string;
  sizeBytes: number | null;
  createdAt: string;
}

export interface DebtorDocumentListResponse {
  items: DebtorDocument[];
  total: number;
}

export interface DocumentCategoryOption {
  value: string;
  label: string;
}

export interface DebtorStatement {
  id: string;
  debtorId: string;
  portfolioId: string;
  organizationId: string;
  organizationName: string;
  creditId: string | null;
  creditNumber: string | null;
  cutoffDate: string;
  documentId: string;
  createdAt: string;
}

export interface DebtorStatementListResponse {
  items: DebtorStatement[];
  total: number;
}
