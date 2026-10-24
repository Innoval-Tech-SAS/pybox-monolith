import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import type { CreatePortfolioResult } from "@/types/companies/company-types";
import { openNotificationStream } from "@/utils/notification-stream";
import { useOrgModule } from "./use-org-module";

export type CsvUploadMode = "append" | "update";

export const useUploadPortfolioCsv = (mode: CsvUploadMode) => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const { orgId, buildOrgPath } = useOrgModule();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<CreatePortfolioResult | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  const processingKey = `portfolioCsvProcessing_${portfolioId}_${mode}`;
  const [processing, setProcessing] = useState(
    () => sessionStorage.getItem(processingKey) === "true",
  );

  const handleReset = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    formRef.current?.reset();
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!portfolioId) {
      toastError("Error", "No se pudo identificar el portafolio.");
      return;
    }
    if (!selectedFile) {
      toastError("Validación", "Debes adjuntar el archivo CSV.");
      return;
    }

    const endpoint = mode === "append"
      ? `/portfolios/upload-csv/append?portfolioId=${portfolioId}`
      : `/portfolios/upload-csv/update?portfolioId=${portfolioId}`;

    const data = new FormData();
    data.set("file", selectedFile);

    setSubmitting(true);
    apiClient<unknown>(endpoint, { method: "POST", body: data })
      .then(() => {
        sessionStorage.setItem(processingKey, "true");
        setProcessing(true);
      })
      .catch(() => {
        toastError("Error", "No se pudo iniciar la carga. Intenta de nuevo.");
      })
      .finally(() => setSubmitting(false));
  };

  useEffect(() => {
    if (!processing || !portfolioId) return;
    if (!sessionStorage.getItem("user")) return;

    const es = openNotificationStream();
    es.addEventListener("notification", (e) => {
      try {
        const notif: AppNotification = JSON.parse(e.data);
        if (notif.category === "portfolio") {
          sessionStorage.removeItem(processingKey);
          setProcessing(false);
          navigate(buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }));
        }
      } catch {
        // malformed event
      }
    });
    es.onerror = () => {};
    return () => es.close();
  }, [processing, portfolioId, orgId, processingKey, navigate, buildOrgPath]);

  const handleDismiss = useCallback(() => {
    sessionStorage.removeItem(processingKey);
    setProcessing(false);
    navigate(buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }));
  }, [navigate, portfolioId, buildOrgPath, processingKey]);

  return {
    orgId,
    portfolioId,
    selectedFile, setSelectedFile,
    submitting,
    processing,
    result,
    formRef,
    handleReset,
    handleSubmit,
    handleDismiss,
  };
};
