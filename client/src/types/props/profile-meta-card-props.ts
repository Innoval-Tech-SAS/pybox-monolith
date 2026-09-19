import type { ReactNode } from "react";
import type { BadgeColor } from "@/types/props/badge-props";

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
  /** Color semántico de <Badge> para role-badge/hierarchy-badge (Fase 9 de la auditoría). */
  badgeColor: BadgeColor;
  containerClass: string;
  iconClass: string;
  textClass: string;
  dotClass: string;
}
