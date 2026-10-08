import { createContext } from "react";
import type { OrgModuleContextType } from "@/types/contexts/org-module-context-type";

export const OrgModuleContext = createContext<OrgModuleContextType | undefined>(undefined);
