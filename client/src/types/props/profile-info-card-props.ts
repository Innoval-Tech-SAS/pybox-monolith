export interface ProfileInfoCardProps {
  email: string;
  phone?: string;
  nationality?: string;
  documentType?: string;
  documentNumber?: string;
}

export interface ProfileInfoField {
  label: string;
  value: string;
  key: string;
  colSpan?: boolean;
}
