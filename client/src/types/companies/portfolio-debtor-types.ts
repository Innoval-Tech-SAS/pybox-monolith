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
