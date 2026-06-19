import { useContext } from "react";
import { OrgModuleContext } from "../contexts/org-module-context";

export const useOrgModule = () => {
  const context = useContext(OrgModuleContext);
  if (!context) {
    throw new Error("useOrgModule must be used within an OrgModuleProvider");
  }
  return context;
};
