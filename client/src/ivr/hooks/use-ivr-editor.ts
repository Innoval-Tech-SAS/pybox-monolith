import { useContext } from "react";
import { IvrEditorContext } from "@/ivr/contexts/ivr-editor-context";

export const useIvrEditor = () => {
  const context = useContext(IvrEditorContext);
  if (!context) {
    throw new Error("useIvrEditor must be used within an IvrEditorContext.Provider");
  }
  return context;
};
