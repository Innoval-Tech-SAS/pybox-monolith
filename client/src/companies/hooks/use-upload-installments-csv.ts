import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import { openNotificationStream } from "@/utils/notification-stream";
import { useOrgModule } from "./use-org-module";

// Hook separado de useUploadPortfolioCsv a propósito: es una carga distinta
// (plan de cuotas de créditos ya existentes), no un modo más del importador de
// portafolio.
export const useUploadInstallmentsCsv = () => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const { buildOrgPath } = useOrgModule();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  const processingKey = `installmentsCsvProcessing_${portfolioId}`;
  const [processing, setProcessing] = useState(
    () => sessionStorage.getItem(processingKey) === "true",
  );

  const handleReset = useCallback(() => {
    setSelectedFile(null);
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

    const data = new FormData();
    data.set("file", selectedFile);

    setSubmitting(true);
    apiClient(`/portfolios/upload-csv/installments?portfolioId=${portfolioId}`, { method: "POST", body: data })
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
  }, [processing, portfolioId, processingKey, navigate, buildOrgPath]);

  const handleDismiss = useCallback(() => {
    sessionStorage.removeItem(processingKey);
    setProcessing(false);
    navigate(buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }));
  }, [navigate, portfolioId, buildOrgPath, processingKey]);

  return {
    portfolioId,
    selectedFile, setSelectedFile,
    submitting,
    processing,
    formRef,
    handleReset,
    handleSubmit,
    handleDismiss,
  };
};
