import type {
  HomeAction,
  HomeMetric,
  HomeRole,
  HomeScope,
} from "@/types/home/home-types";

export type HomeShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  metrics: HomeMetric[];
  actions: HomeAction[];
};

export type RoleScopeHomeProps = {
  role: HomeRole;
  scope: HomeScope;
};
