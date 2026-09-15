import { createContext } from "react";
import type { SessionContextType } from "@/types/contexts/session-context-type";

export const SessionContext = createContext<SessionContextType | undefined>(undefined);
