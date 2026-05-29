export interface PortfolioDebtor {
  id: number;
  fullName: string;
  documentType: string;
  documentNumber: string;
  debtorType: string;
}

export interface DebtorAddress {
  id: number;
  address: string;
  city: string;
  state: string;
  country: string;
  addressType: string;
}

export interface DebtorContactMethod {
  id: number;
  contactType: string;
  contactValue: string;
}

export interface DebtorCreditSummary {
  id: number;
  creditNumber: string;
  creditType: string;
  totalCreditBalance: number;
  daysOverdueAtCutoff: number;
}

export interface DebtorProfile {
  debtor: PortfolioDebtor;
  addresses: DebtorAddress[];
  contactMethods: DebtorContactMethod[];
  credits: DebtorCreditSummary[];
}

export interface PortfolioDebtorsResponse {
  items: PortfolioDebtor[];
  total: number;
  page: number;
  pages: number;
}
