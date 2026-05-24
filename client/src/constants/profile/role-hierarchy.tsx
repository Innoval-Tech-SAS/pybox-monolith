import { Crown, Headphones, Shield, ShieldCheck, User, Users } from "lucide-react";
import type { HierarchyTier } from "@/types/props/profile-meta-card-props";

export const ROLE_HIERARCHY: Record<string, HierarchyTier> = {
  "ADMINISTRADOR|GLOBAL": {
    tier: 1,
    label: "Admin Global",
    icon: <Crown size={13} />,
    containerClass: "bg-amber-50 border border-amber-200 dark:bg-amber-500/10 dark:border-amber-500/30",
    iconClass: "text-amber-600 dark:text-amber-400",
    textClass: "text-amber-700 dark:text-amber-400",
    dotClass: "bg-amber-500",
  },
  "ATENCION AL CLIENTE|GLOBAL": {
    tier: 2,
    label: "Soporte Global",
    icon: <ShieldCheck size={13} />,
    containerClass: "bg-violet-50 border border-violet-200 dark:bg-violet-500/10 dark:border-violet-500/30",
    iconClass: "text-violet-600 dark:text-violet-400",
    textClass: "text-violet-700 dark:text-violet-400",
    dotClass: "bg-violet-500",
  },
  "ADMINISTRADOR|ORGANIZATION": {
    tier: 3,
    label: "Administrador",
    icon: <Shield size={13} />,
    containerClass: "bg-blue-50 border border-blue-200 dark:bg-blue-500/10 dark:border-blue-500/30",
    iconClass: "text-blue-600 dark:text-blue-400",
    textClass: "text-blue-700 dark:text-blue-400",
    dotClass: "bg-blue-500",
  },
  "ATENCION AL CLIENTE|ORGANIZATION": {
    tier: 4,
    label: "Soporte",
    icon: <Headphones size={13} />,
    containerClass: "bg-teal-50 border border-teal-200 dark:bg-teal-500/10 dark:border-teal-500/30",
    iconClass: "text-teal-600 dark:text-teal-400",
    textClass: "text-teal-700 dark:text-teal-400",
    dotClass: "bg-teal-500",
  },
  "USUARIO ORGANIZACIÓN|ORGANIZATION": {
    tier: 5,
    label: "Usuario",
    icon: <Users size={13} />,
    containerClass: "bg-sky-50 border border-sky-200 dark:bg-sky-500/10 dark:border-sky-500/30",
    iconClass: "text-sky-600 dark:text-sky-400",
    textClass: "text-sky-700 dark:text-sky-400",
    dotClass: "bg-sky-400",
  },
  "USUARIO|SELF": {
    tier: 6,
    label: "Usuario",
    icon: <User size={13} />,
    containerClass: "bg-gray-100 border border-gray-200 dark:bg-gray-700 dark:border-gray-600",
    iconClass: "text-gray-500 dark:text-gray-400",
    textClass: "text-gray-600 dark:text-gray-400",
    dotClass: "bg-gray-400",
  },
};

export const getRoleHierarchy = (role?: string, scope?: string): HierarchyTier | null => {
  if (!role || !scope) return null;
  return ROLE_HIERARCHY[`${role}|${scope}`] ?? null;
};
