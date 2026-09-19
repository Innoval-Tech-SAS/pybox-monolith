import { HelmetProvider } from "react-helmet-async";
import type { ChildrenProps } from "@/types/props/provider-props";

export const AppWrapper = ({ children }: ChildrenProps) => (
  <HelmetProvider>{children}</HelmetProvider>
);
