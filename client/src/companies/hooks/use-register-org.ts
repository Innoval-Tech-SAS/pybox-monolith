import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { RepresentativeMode } from "@/types/companies/company-types";
import { validateOrgDocumentFile } from "../utils/org-file-validation";

export const useRegisterOrg = () => {
  const { success, warning } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Org fields
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [fiscalDocNumber, setFiscalDocNumber] = useState("");
  const [description, setDescription] = useState("");

  // Files
  const [mercantileFile, setMercantileFile] = useState<File | null>(null);
  const [mercantileError, setMercantileError] = useState<string | null>(null);
  const [repFile, setRepFile] = useState<File | null>(null);
  const [repFileError, setRepFileError] = useState<string | null>(null);

  // Representative mode
  const [repMode, setRepMode] = useState<RepresentativeMode>("self");

  // SELECT mode
  const [selectedUserId, setSelectedUserId] = useState("");

  // CREATE mode
  const [repFirstname, setRepFirstname] = useState("");
  const [repLastname, setRepLastname] = useState("");
  const [repEmail, setRepEmail] = useState("");
  const [repDocType, setRepDocType] = useState("");
  const [repDocNumber, setRepDocNumber] = useState("");

  const formRef = useRef<HTMLFormElement>(null);

  const handleMercantileFileChange = useCallback((file: File | null) => {
    const err = validateOrgDocumentFile(file, "documento mercantil");
    setMercantileError(err);
    setMercantileFile(err ? null : file);
  }, []);

  const handleRepFileChange = useCallback((file: File | null) => {
    const err = validateOrgDocumentFile(file, "documento del representante");
    setRepFileError(err);
    setRepFile(err ? null : file);
  }, []);

  const handleReset = useCallback(() => {
    setName("");
    setCountry("");
    setFiscalDocNumber("");
    setDescription("");
    setMercantileFile(null);
    setMercantileError(null);
    setRepFile(null);
    setRepFileError(null);
    setRepMode("self");
    setSelectedUserId("");
    setRepFirstname("");
    setRepLastname("");
    setRepEmail("");
    setRepDocType("");
    setRepDocNumber("");
    formRef.current?.reset();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const mercantileErr = validateOrgDocumentFile(mercantileFile, "documento mercantil");
      if (mercantileErr) { setMercantileError(mercantileErr); warning("Validación", mercantileErr); return; }

      const repFileErr = validateOrgDocumentFile(repFile, "documento del representante");
      if (repFileErr) { setRepFileError(repFileErr); warning("Validación", repFileErr); return; }

      const data = new FormData();
      data.set("name", name);
      data.set("country", country);
      data.set("representative_mode", repMode);
      if (fiscalDocNumber) data.set("fiscal_document_number", fiscalDocNumber);
      if (description) data.set("description", description);
      data.set("mercantile_document_file", mercantileFile!);
      data.set("representative_document_file", repFile!);

      if (repMode === "select") {
        if (!selectedUserId) { warning("Validación", "Selecciona un representante legal."); return; }
        data.set("representative_user_id", selectedUserId);
      } else if (repMode === "create") {
        data.set("rep_firstname", repFirstname);
        data.set("rep_lastname", repLastname);
        data.set("rep_email", repEmail);
        data.set("rep_document_type", repDocType);
        data.set("rep_document_number", repDocNumber);
      }

      const result = await apiClient("/organizations/register", { method: "POST", body: data });
      if (result) {
        success("Organización creada", `${result.name} fue registrada correctamente.`);
        navigate("/my-companies");
      }
    } catch {
      // handled by apiClient
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    name, setName,
    country, setCountry,
    fiscalDocNumber, setFiscalDocNumber,
    description, setDescription,
    mercantileFile, mercantileError, handleMercantileFileChange,
    repFile, repFileError, handleRepFileChange,
    repMode, setRepMode,
    selectedUserId, setSelectedUserId,
    repFirstname, setRepFirstname,
    repLastname, setRepLastname,
    repEmail, setRepEmail,
    repDocType, setRepDocType,
    repDocNumber, setRepDocNumber,
    formRef,
    handleSubmit,
    handleReset,
  };
};
