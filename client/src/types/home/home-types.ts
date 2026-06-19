import type { ReactNode } from "react";

import type { User } from "@/types/auth/user";
import { Role, Scope } from "@/types/auth/role";

export type HomeRole = Role;
export type HomeScope = Scope;
export type HomeContextSource = "session" | "default";
export type HomeTone = "primary" | "success" | "warning" | "info" | "light";

export type RoleAssignment = {
  role?: string;
  scope?: string;
};

export type SessionUser = Partial<User> & {
  scope?: string;
  userRole?: string;
  userScope?: string;
  roles?: RoleAssignment[];
  roleAssignments?: RoleAssignment[];
};

export type HomeContext = {
  role: HomeRole;
  scope: HomeScope;
  source: HomeContextSource;
  user: SessionUser | null;
  status: "loading" | "ready";
};

export type HomeMetric = {
  label: string;
  value: string;
  helper: string;
  tone: HomeTone;
};

export type HomeAction = {
  title: string;
  description: string;
  icon: ReactNode;
  tone: HomeTone;
};
