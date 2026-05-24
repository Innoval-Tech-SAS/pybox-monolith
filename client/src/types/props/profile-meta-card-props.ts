import type { ReactNode } from "react";

export interface ProfileMetaCardProps {
  fullName: string;
  role?: string;
  scope?: string;
  avatarUrl?: string;
}

export interface HierarchyTier {
  label: string;
  icon: ReactNode;
  tier: number;
  containerClass: string;
  iconClass: string;
  textClass: string;
  dotClass: string;
}
