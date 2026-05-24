import type { OrgSessionEntry } from "@/types/auth/user";

export interface ProfileInfoCardProps {
  email: string;
  documentType?: string;
  documentNumber?: string;
  orgs?: Record<string, OrgSessionEntry>;
}

export interface ProfileInfoField {
  label: string;
  value: string;
  key: string;
  colSpan?: boolean;
}
