import type { ReactNode } from "react";

export interface ChildrenProps {
  children: ReactNode;
}

export interface ToastProviderProps extends ChildrenProps {
  duration?: number;
}
