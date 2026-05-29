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

export interface DebtorDetail {
  id: number;
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
  id: number;
  creditNumber: string;
  creditType: string;
  disbursedDate: string;
  totalCreditBalance: number;
  overduePrincipalBalance: number;
  daysOverdueAtCutoff: number;
  overdueInstallments: number;
  pendingInstallments: number;
}

export interface PortfolioDebtorsResponse {
  items: PortfolioDebtor[];
  total: number;
  page: number;
  pageSize: number;
}
